import os
import json
from tkinter import messagebox

def get_mappings_folder():
    """
    Return the path to the mappings folder, creating it if necessary.
    """
    folder = os.path.join(os.path.dirname(__file__), "mappings")
    os.makedirs(folder, exist_ok=True)
    return folder

def list_mapping_files(folder):
    """
    List all JSON mapping files in the given folder.
    """
    return [f for f in os.listdir(folder) if f.endswith(".json")]

def show_error(message):
    """
    Display an error message dialog.
    """
    messagebox.showerror("Error", message)

def validate_mapping(mapping):
    """
    Validate that the mapping is a dict with non-empty pattern and folder strings.
    """
    if not isinstance(mapping, dict):
        return False
    for pattern, folder in mapping.items():
        if not pattern or not folder:
            return False
    return True

def load_json_file(path):
    """
    Load and return JSON data from a file.
    """
    with open(path, "r") as f:
        return json.load(f)

def save_json_file(path, data):
    """
    Save data as JSON to a file.
    """
    with open(path, "w") as f:
        json.dump(data, f, indent=4)