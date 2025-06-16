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
    @staticmethod
    def load_json_file(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_json_file(path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def validate_mapping(mapping):
        # Basic validation: mapping should be a dict of str:str
        if not isinstance(mapping, dict):
            return False
        for k, v in mapping.items():
            if not isinstance(k, str) or not isinstance(v, str):
                return False
        return True

    @staticmethod
    def load_mapping(path):
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
