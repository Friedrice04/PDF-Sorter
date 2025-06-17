import os
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog

class NewMappingDialog(simpledialog.Dialog):
    def __init__(self, parent, title):
        self.mapping_name = None
        self.import_selected = False
        self.import_path = None
        super().__init__(parent, title)

    def body(self, master):
        ttk.Label(master, text="Mapping Name:").grid(row=0, column=0, sticky="w")
        self.name_entry = ttk.Entry(master)
        self.name_entry.grid(row=0, column=1, sticky="ew")
        self.name_entry.focus_set()

        self.import_var = ttk.IntVar()
        self.import_check = ttk.Checkbutton(master, text="Import from existing mapping", variable=self.import_var, command=self._toggle_import)
        self.import_check.grid(row=1, column=0, columnspan=2, sticky="w")

        self.import_btn = ttk.Button(master, text="Browse...", command=self._browse_import, state="disabled")
        self.import_btn.grid(row=2, column=0, columnspan=2, sticky="w")

        master.grid_columnconfigure(1, weight=1)
        return self.name_entry

    def _toggle_import(self):
        if self.import_var.get():
            self.import_btn.config(state="normal")
        else:
            self.import_btn.config(state="disabled")
            self.import_path = None

    def _browse_import(self):
        path = filedialog.askopenfilename(
            title="Select Mapping File",
            filetypes=[("JSON Files", "*.json")]
        )
        if path:
            self.import_path = path

    def validate(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a mapping name.", parent=self)
            return False
        if self.import_var.get() and not self.import_path:
            messagebox.showerror("Error", "Please select a mapping file to import.", parent=self)
            return False
        return True

    def apply(self):
        self.mapping_name = self.name_entry.get().strip()
        self.import_selected = bool(self.import_var.get())
        self.import_path = self.import_path

class PatternDestDialog(simpledialog.Dialog):
    def __init__(self, parent, title, template_dir, destinations, initial_pattern=None, initial_dest=None):
        self.pattern = None
        self.dest = None
        self.template_dir = template_dir
        self.destinations = destinations
        self.initial_pattern = initial_pattern
        self.initial_dest = initial_dest
        super().__init__(parent, title)

    def body(self, master):
        ttk.Label(master, text="Pattern:").grid(row=0, column=0, sticky="w")
        self.pattern_entry = ttk.Entry(master)
        self.pattern_entry.grid(row=0, column=1, sticky="ew")
        if self.initial_pattern:
            self.pattern_entry.insert(0, self.initial_pattern)

        ttk.Label(master, text="Destination:").grid(row=1, column=0, sticky="w")
        self.dest_combo = ttk.Combobox(master, values=self.destinations, state="readonly")
        self.dest_combo.grid(row=1, column=1, sticky="ew")
        if self.initial_dest:
            self.dest_combo.set(self.initial_dest)
        elif self.destinations:
            self.dest_combo.set(self.destinations[0])

        master.grid_columnconfigure(1, weight=1)
        return self.pattern_entry

    def validate(self):
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
        self.pattern = self.pattern_entry.get().strip()
        self.dest = self.dest_combo.get().strip()