import os
import shutil
import fitz  # PyMuPDF

from . import utils

class Sorter:
    def __init__(self, mapping_path, progress_callback=None, status_callback=None):
        self.mapping_path = mapping_path
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.mapping_data = self.load_mapping()

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

    def read_pdf_text(self, file_path):
        """
        Reads and returns the text content from a PDF file.
        Returns an empty string if the file cannot be read.
        """
        try:
            with fitz.open(file_path) as doc:
                text = "".join(page.get_text() for page in doc)
                return text
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"Error reading {os.path.basename(file_path)}: {e}")
            return ""

    def sort_files(self, folders_to_sort, deep_audit=False):
        total_files_sorted = 0
        total_files_scanned = 0

        for folder in folders_to_sort:
            root = folder  # In this simplified version, we sort each folder individually
            if self.status_callback:
                self.status_callback(f"Sorting folder: {root}")

            for filename in os.listdir(root):
                if filename.startswith('.'):
                    continue  # Skip hidden files
                
                total_files_scanned += 1
                file_path = os.path.join(root, filename)
                if os.path.isdir(file_path):
                    # Skip directories in this version
                    continue
                
                if filename.lower().endswith('.pdf'):
                    if self.status_callback:
                        self.status_callback(f"Scanning: {file_path}")

                    text = self.read_pdf_text(file_path)
                    if not text:
                        continue

                    try:
                        destination_folder = self.find_destination(text)

                        if destination_folder:
                            destination_path = os.path.join(self.template_dir, destination_folder)
                            os.makedirs(destination_path, exist_ok=True)
                            shutil.move(file_path, os.path.join(destination_path, filename))
                            total_files_sorted += 1
                            if self.progress_callback:
                                self.progress_callback(total_files_sorted, total_files_scanned)
                        else:
                            if self.status_callback:
                                self.status_callback(f"No match found for: {filename}")
                    except Exception as e:
                        if self.status_callback:
                            self.status_callback(f"Error processing {filename}: {e}")

        if deep_audit:
            if self.status_callback:
                self.status_callback("Deep audit not implemented in this version.")