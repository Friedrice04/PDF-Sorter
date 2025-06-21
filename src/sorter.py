import os
import shutil
import fitz  # PyMuPDF

from src import utils

# Attempt to import OCR libraries. If they fail, OCR will be disabled.
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

class Sorter:
    def __init__(self, mapping_path, progress_callback=None, status_callback=None):
        self.mapping_path = mapping_path
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.mapping_data = self.load_mapping()
        # The template directory is named after the mapping file (without .json) + "_template"
        self.template_dir = os.path.splitext(self.mapping_path)[0] + "_template"
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)

    def load_mapping(self):
        """
        Load mapping from the JSON file specified by mapping_path.
        """
        if self.status_callback:
            self.status_callback(f"Loading mapping from {self.mapping_path}")
        data = utils.MappingUtils.load_mapping(self.mapping_path)
        if self.status_callback:
            self.status_callback(f"Mapping loaded from {self.mapping_path}")
        return data

    def read_pdf_text(self, file_path, first_page_only=False):
        """
        Reads text from a PDF. Can be set to read only the first page.
        If that fails (e.g., for a scanned PDF), it falls back to OCR.
        """
        text = ""
        try:
            # 1. First, try direct text extraction
            with fitz.open(file_path) as doc:
                if not doc:
                    return ""
                
                if first_page_only:
                    text = doc[0].get_text().strip()
                else:
                    text = "".join(page.get_text() for page in doc).strip()
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"Error reading {os.path.basename(file_path)}: {e}")
            return ""

        # 2. If no text was found, fall back to OCR if available
        if not text and OCR_AVAILABLE:
            if self.status_callback:
                self.status_callback(f"No text layer in {os.path.basename(file_path)}. Attempting OCR...")
            try:
                ocr_texts = []
                with fitz.open(file_path) as doc:
                    if not doc:
                        return ""
                    
                    # Determine which pages to scan based on the flag
                    pages_to_scan = [doc[0]] if first_page_only and len(doc) > 0 else doc

                    for i, page in enumerate(pages_to_scan):
                        if self.status_callback:
                            # Adjust status message for single page scan
                            page_count = len(pages_to_scan)
                            self.status_callback(f"OCR page {i + 1}/{page_count} of {os.path.basename(file_path)}...")
                        # Render page to an image (pixmap) at high DPI for better accuracy
                        pix = page.get_pixmap(dpi=300)
                        # Convert pixmap to a PIL Image
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        # Use Tesseract to do OCR on the image.
                        # NOTE: This requires Tesseract-OCR to be installed on your system.
                        page_text = pytesseract.image_to_string(img)
                        ocr_texts.append(page_text)
                text = "\n".join(ocr_texts)
            except pytesseract.TesseractNotFoundError:
                if self.status_callback:
                    self.status_callback("Tesseract not found. OCR unavailable. Please install Tesseract.")
                return "" # Return empty string if Tesseract is not found
            except Exception as e:
                if self.status_callback:
                    self.status_callback(f"An error occurred during OCR: {e}")
                return ""
        elif not text and not OCR_AVAILABLE:
             if self.status_callback:
                self.status_callback(f"No text in {os.path.basename(file_path)}, and OCR libraries not installed.")

        return text

    def find_destination(self, text):
        """
        Finds the destination folder by checking for keywords in the text.
        The search is case-insensitive and normalized to handle OCR quirks.
        """
        # Normalize the text from the PDF: replace newlines/tabs with spaces,
        # collapse multiple spaces, and convert to lowercase.
        normalized_text = ' '.join(text.split()).lower()

        for phrase, destination in self.mapping_data.items():
            # Normalize the mapping phrase in the same way.
            normalized_phrase = ' '.join(phrase.split()).lower()
            
            if normalized_phrase in normalized_text:
                if self.status_callback:
                    # Add a debug message to show exactly what matched.
                    self.status_callback(f"Found a match for keyword: '{normalized_phrase}'")
                return destination
        return None

    def sort_files(self, folders_to_sort, deep_audit=False, first_page_only=False):
        total_files_sorted = 0
        total_files_scanned = 0

        for folder in folders_to_sort:
            if not os.path.isdir(folder):
                continue
            
            # In this version, we only scan the top-level of the provided folder
            root = folder 
            if self.status_callback:
                self.status_callback(f"Sorting folder: {root}")

            for filename in os.listdir(root):
                file_path = os.path.join(root, filename)
                
                if os.path.isdir(file_path):
                    # Skip directories in this version
                    continue
                
                if filename.lower().endswith('.pdf'):
                    total_files_scanned += 1
                    if self.status_callback:
                        self.status_callback(f"Scanning: {file_path}")

                    text = self.read_pdf_text(file_path, first_page_only=first_page_only)
                    if not text:
                        continue

                    try:
                        destination_folder = self.find_destination(text)

                        if destination_folder:
                            destination_path = os.path.join(self.template_dir, destination_folder)
                            os.makedirs(destination_path, exist_ok=True)
                            shutil.move(file_path, os.path.join(destination_path, filename))
                            total_files_sorted += 1
                            if self.status_callback:
                                self.status_callback(f"Moved: {filename} -> {destination_folder}")
                        else:
                            if self.status_callback:
                                self.status_callback(f"No match found for: {filename}")
                                # Print the NORMALIZED text for easier debugging
                                debug_text = ' '.join(text.split()).lower()
                                if len(debug_text) > 1000:
                                    debug_text = debug_text[:1000] + "..."
                                self.status_callback(f"--- Normalized Text Read from {filename} ---\n{debug_text}\n---------------------------------")
                    except Exception as e:
                        if self.status_callback:
                            self.status_callback(f"Error processing {filename}: {e}")

        if deep_audit:
            if self.status_callback:
                self.status_callback("Deep audit not yet implemented.")
        
        if self.status_callback:
            self.status_callback(f"Sort complete. Scanned: {total_files_scanned}, Moved: {total_files_sorted}")