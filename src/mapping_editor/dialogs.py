"""
dialogs.py

Dialog classes for FileSorter:
- NewMappingDialog: Create a new mapping, optionally importing from an existing mapping file.
- PatternDestDialog: Edit or add a pattern/destination mapping, with user-friendly layout and help.

Author: Your Name
"""

import os
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog

class NewMappingDialog(simpledialog.Dialog):
    """
    Dialog for creating a new mapping file, with optional import from an existing mapping.
    Shows the selected import file for user clarity.
    """
    def __init__(self, parent, title):
        self.mapping_name = None
        self.import_selected = False
        self.import_path = None
        super().__init__(parent, title)

    def body(self, master):
        """
        Build the dialog UI.
        """
        frame = ttk.Frame(master)
        frame.grid(sticky="nsew")
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        ttk.Label(frame, text="Mapping Name:").grid(row=0, column=0, sticky="w")
        self.name_entry = ttk.Entry(frame)
        self.name_entry.grid(row=0, column=1, sticky="ew")
        self.name_entry.focus_set()

        self.import_var = tk.IntVar()
        self.import_check = ttk.Checkbutton(
            frame, text="Import from existing mapping", variable=self.import_var, command=self._toggle_import
        )
        self.import_check.grid(row=1, column=0, columnspan=2, sticky="w")

        self.import_btn = ttk.Button(frame, text="Browse...", command=self._browse_import, state="disabled")
        self.import_btn.grid(row=2, column=0, sticky="w")

        # Label to show selected file
        self.import_file_label = ttk.Label(frame, text="", foreground="#555")
        self.import_file_label.grid(row=2, column=1, sticky="w")

        return self.name_entry

    def _toggle_import(self):
        """
        Enable or disable the import button and clear the file label as needed.
        """
        if self.import_var.get():
            self.import_btn.config(state="normal")
        else:
            self.import_btn.config(state="disabled")
            self.import_path = None
            self.import_file_label.config(text="")

    def _browse_import(self):
        """
        Open a file dialog to select a mapping file to import, and display the file name.
        """
        path = filedialog.askopenfilename(
            title="Select Mapping File",
            filetypes=[("JSON Files", "*.json")]
        )
        if path:
            self.import_path = path
            # Show only the file name for clarity
            self.import_file_label.config(text=os.path.basename(path))
        else:
            self.import_file_label.config(text="")

    def validate(self):
        """
        Validate user input before closing the dialog.
        """
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a mapping name.", parent=self)
            return False
        if self.import_var.get() and not self.import_path:
            messagebox.showerror("Error", "Please select a mapping file to import.", parent=self)
            return False
        return True

    def apply(self):
        """
        Save the dialog results.
        """
        self.mapping_name = self.name_entry.get().strip()
        self.import_selected = bool(self.import_var.get())
        self.import_path = self.import_path

class PatternDestDialog(simpledialog.Dialog):
    """
    Dialog for adding or editing a pattern/destination mapping.
    Provides a clean, user-friendly layout with help text.
    """
    def __init__(self, parent, title, template_dir, destinations, initial_pattern=None, initial_dest=None):
        self.pattern = None
        self.dest = None
        self.template_dir = template_dir
        self.destinations = destinations
        self.initial_pattern = initial_pattern
        self.initial_dest = initial_dest
        super().__init__(parent, title)

    def body(self, master):
        """
        Build the dialog UI.
        """
        frame = ttk.Frame(master, padding=16)
        frame.grid(sticky="nsew")
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Pattern
        ttk.Label(frame, text="Pattern:").grid(row=0, column=0, sticky="e", pady=(0, 8), padx=(0, 8))
        self.pattern_entry = ttk.Entry(frame)
        self.pattern_entry.grid(row=0, column=1, sticky="ew", pady=(0, 8))
        self.pattern_entry.insert(0, self.initial_pattern or "")
        self.pattern_entry.focus_set()

        # Destination
        ttk.Label(frame, text="Destination:").grid(row=1, column=0, sticky="e", pady=(0, 8), padx=(0, 8))
        self.dest_combo = ttk.Combobox(frame, values=self.destinations, state="readonly")
        self.dest_combo.grid(row=1, column=1, sticky="ew", pady=(0, 8))
        if self.initial_dest:
            self.dest_combo.set(self.initial_dest)
        elif self.destinations:
            self.dest_combo.set(self.destinations[0])

        # Info/help text
        info = (
            "• Use wildcards like * and ? in patterns (e.g. *.jpg, report_*.pdf)\n"
            "• Destination is relative to the template directory"
        )
        info_label = ttk.Label(frame, text=info, foreground="#666", font=("Segoe UI", 9, "italic"), anchor="w", justify="left")
        info_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 0))

        self.resizable(True, False)
        # Set initial geometry based on destination length
        dest = self.initial_dest if self.initial_dest else (self.destinations[0] if self.destinations else "")
        min_width = 400
        width = max(min_width, 7 * len(dest) + 160)
        self.after(10, lambda: self.geometry(f"{width}x160"))

        return self.pattern_entry

    def validate(self):
        """
        Validate user input before closing the dialog.
        """
        pattern = self.pattern_entry.get().strip()
        dest = self.dest_combo.get().strip()
        if not pattern:
            messagebox.showerror("Error", "Please enter a pattern.", parent=self)
            return False
        if not dest:
            messagebox.showerror("Error", "Please select a destination.", parent=self)
            return False
        return True

    def apply(self):
        """
        Save the dialog results.
        """
        self.pattern = self.pattern_entry.get().strip()
        self.dest = self.dest_combo.get().strip()

# Simple tooltip helper for user-friendliness
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert") if hasattr(self.widget, "bbox") else (0, 0, 0, 0)
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, justify="left",
            background="#ffffe0", relief="solid", borderwidth=1,
            font=("Segoe UI", 9)
        )
        label.pack(ipadx=4, ipady=2)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()