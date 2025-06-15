import os
import json
import tkinter as tk
from tkinter import messagebox


def show_error(message):
    """
    Display an error message dialog.
    """
    messagebox.showerror("Error", message)


class MappingUtils:
    """
    Utility class for handling mapping file operations and validation.
    """
    
    @staticmethod
    def get_mappings_folder():
        """
        Return the path to the mappings folder, creating it if necessary.
        """
        folder = os.path.join(os.path.dirname(__file__), "mappings")
        os.makedirs(folder, exist_ok=True)
        return folder

    @staticmethod
    def list_mapping_files(folder=None):
        """
        List all JSON mapping files in the given folder.
        """
        if folder is None:
            folder = MappingUtils.get_mappings_folder()
        return [f for f in os.listdir(folder) if f.endswith(".json")]
    
    @staticmethod
    def load_json_file(path):
        """
        Load and return JSON data from a file.
        """
        with open(path, "r") as f:
            return json.load(f)

    @staticmethod
    def save_json_file(path, data):
        """
        Save data as JSON to a file.
        """
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
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
