import os
import sys
import json
import tkinter as tk
from tkinter import messagebox

# --- Constants ---
SETTINGS_FILE = "settings.json"
LAST_MAPPING_KEY = "last_mapping_file"
MAPPINGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "mappings"))

# --- Settings Functions ---
def load_settings():
    """Loads the application settings from settings.json."""
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_settings(settings):
    """Saves the application settings to settings.json."""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

class MappingUtils:
    """A utility class for handling mapping files."""

    @staticmethod
    def get_available_mappings():
        """Returns a sorted list of available .json mapping files."""
        os.makedirs(MAPPINGS_DIR, exist_ok=True)
        return sorted([f for f in os.listdir(MAPPINGS_DIR) if f.endswith(".json")])

    @staticmethod
    def is_valid_mapping_file(file_path):
        """Checks if a file is a valid, non-empty JSON file."""
        if not file_path or not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return False
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, UnicodeDecodeError):
            return False

    @staticmethod
    def load_mapping(file_path):
        """Loads mapping data from a JSON file, migrating old format if necessary."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Check for old format and migrate.
            # The first value in the dict will be a string in the old format,
            # and a dictionary in the new format.
            if data and isinstance(next(iter(data.values())), str):
                migrated_data = {}
                for phrase, dest in data.items():
                    # Create a default name from the phrase for backward compatibility
                    default_name = phrase.replace("_", " ").replace("-", " ").title()
                    migrated_data[phrase] = {"name": default_name, "dest": dest}
                return migrated_data
            
            return data
        except (FileNotFoundError, json.JSONDecodeError, StopIteration):
            return {}

    @staticmethod
    def save_mapping(file_path, data):
        """Saves mapping data to a JSON file."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

# --- UI Helpers ---
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
