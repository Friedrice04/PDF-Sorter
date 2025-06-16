import os
import shutil
import fnmatch
import json

class FileMapping:
    """
    Handles loading and validating file mapping from JSON.
    """
    def __init__(self, mapping_path):
        self.mapping = self.load_mapping(mapping_path)

    @staticmethod
    def load_mapping(mapping_path):
        """
        Load mapping from a JSON file.
        """
        with open(mapping_path, 'r') as f:
            return json.load(f)

    def get_destination(self, filename):
        """
        Return the destination folder for a given filename based on mapping.
        """
        for pattern, folder in self.mapping.items():
            if fnmatch.fnmatch(filename, pattern):
                return folder
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
                dest_folder = self.mapping.get_destination(filename)
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
                correct_folder = self.mapping.get_destination(filename)
                if correct_folder:
                    correct_path = os.path.join(root_dir, correct_folder)
                    os.makedirs(correct_path, exist_ok=True)
                    current_path = os.path.join(dirpath, filename)
                    target_path = os.path.join(correct_path, filename)
                    if os.path.abspath(current_path) != os.path.abspath(target_path):
                        shutil.move(current_path, target_path)