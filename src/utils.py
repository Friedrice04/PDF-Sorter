import os
import sys
import json
import tkinter as tk
from tkinter import messagebox

# --- Constants ---
SETTINGS_FILE = "settings.json"
LAST_MAPPING_KEY = "last_mapping_file"
MAPPINGS_DIR = os.path.join('src', 'mappings')

# --- Utility Functions ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # When running as a script, the base path is the project root.
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_settings():
    """
    Load settings from the settings.json file.
    """
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}  # Return empty settings if file is corrupt or unreadable
    return {}

def save_settings(settings):
    """
    Save settings to the settings.json file.
    """
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception:
        pass

def show_error(message):
    """
    Display an error message dialog.
    """
    messagebox.showerror("Error", message)

# --- Utility Classes ---
class MappingUtils:
    @staticmethod
    def get_available_mappings():
        """Scans the mappings directory and returns a list of .json mapping files."""
        if not os.path.exists(MAPPINGS_DIR):
            os.makedirs(MAPPINGS_DIR)
            return []
        
        try:
            # List files, filter for .json, and return just the filenames
            mappings = [
                f for f in os.listdir(MAPPINGS_DIR) 
                if f.lower().endswith('.json') and os.path.isfile(os.path.join(MAPPINGS_DIR, f))
            ]
            return mappings
        except Exception:
            return [] # Return empty list on error

    @staticmethod
    def load_mapping(path):
        """Loads a single mapping file."""
        return MappingUtils.load_json_file(path)

    @staticmethod
    def save_mapping(path, mapping):
        MappingUtils.save_json_file(path, mapping)

    @staticmethod
    def is_valid_mapping_file(path):
        try:
            mapping = MappingUtils.load_json_file(path)
            return MappingUtils.validate_mapping(mapping)
        except Exception:
            return False

    @staticmethod
    def get_mappings_folder():
        # You can customize this as needed
        folder = os.path.join(os.getcwd(), "mappings")
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder

    @staticmethod
    def list_mapping_files(folder):
        return [f for f in os.listdir(folder) if f.endswith(".json")]

    @staticmethod
    def show_error(msg):
        from tkinter import messagebox
        messagebox.showerror("Error", msg)

class ToolTip:
    """
    Create a tooltip for a given widget.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_pointerx() + 20
        y = self.widget.winfo_pointery() + 10
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, justify=tk.LEFT,
            background="#ffffe0", relief=tk.SOLID, borderwidth=1,
            font=("tahoma", "8", "normal")
        )
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
