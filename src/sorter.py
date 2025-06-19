import os
import shutil
import fnmatch
import json
import fitz  # PyMuPDF

class FileMapping:
    """
    Handles loading and validating file mapping from JSON.
    The mapping consists of phrases to find in PDF content.
    """
    def __init__(self, mapping_path):
        self.mapping = self.load_mapping(mapping_path)

    @staticmethod
    def load_mapping(mapping_path):
        """
        Load mapping from a JSON file.
        """
        with open(mapping_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_destination_for_pdf(self, file_path):
        """
        Extracts text from a PDF and returns a destination folder if a mapped phrase is found.
        """
        try:
            with fitz.open(file_path) as doc:
                text = ""
                for page in doc:
                    text += page.get_text()
            
            # Make search case-insensitive
            text_lower = text.lower()

            for phrase, folder in self.mapping.items():
                if phrase.lower() in text_lower:
                    return folder
        except Exception:
            # Could be a corrupted PDF or not a PDF at all
            return None
        return None

    def get_destination(self, file_path):
        """
        Return the destination folder for a given file.
        Currently only supports sorting based on PDF content.
        """
        if file_path.lower().endswith('.pdf'):
            return self.get_destination_for_pdf(file_path)
        return None

class FileSorter:
    """
    Main class for sorting files based on mapping.
    """
    def __init__(self, mapping_path):
        self.mapping = FileMapping(mapping_path)

    def _sort_files(self, src_dir, dest_dir):
        """
        Sort files from src_dir into dest_dir based on mapping.
        """
        for filename in os.listdir(src_dir):
            src_path = os.path.join(src_dir, filename)
            if os.path.isfile(src_path):
                dest_folder = self.mapping.get_destination(src_path)
                if dest_folder:
                    dest_path = os.path.join(dest_dir, dest_folder)
                    os.makedirs(dest_path, exist_ok=True)
                    shutil.move(src_path, os.path.join(dest_path, filename))

    def sort_current_directory(self, directory):
        """
        Sort files in the given directory.
        """
        self._sort_files(directory, directory)

    def deep_audit_and_sort(self, root_dir):
        """
        Recursively move misplaced files to their correct folders.
        """
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                current_path = os.path.join(dirpath, filename)
                correct_folder = self.mapping.get_destination(current_path)
                if correct_folder:
                    correct_path = os.path.join(root_dir, correct_folder)
                    os.makedirs(correct_path, exist_ok=True)
                    target_path = os.path.join(correct_path, filename)
                    if os.path.abspath(current_path) != os.path.abspath(target_path):
                        shutil.move(current_path, target_path)