"""
dialogs.py

Dialog classes for FileSorter:
- NewMappingDialog: Create a new mapping, optionally importing from an existing mapping file.
- PatternDestDialog: Edit or add a pattern/destination mapping, with user-friendly layout and help.

Author: Your Name
"""

import os
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox

class BaseDialog(ctk.CTkToplevel):
    """
    A base class for creating themed, frameless, modal dialogs with CustomTkinter.
    """
    def __init__(self, parent, title="Dialog", geometry="450x250"):
        super().__init__(parent)
        self.parent = parent
        self.title_text = title
        self.result = None

        # --- Window Setup ---
        self.geometry(geometry)
        self.overrideredirect(True)

        # Make window rounded by making the background transparent
        TRANSPARENT_COLOR = '#000001'
        self.config(bg=TRANSPARENT_COLOR)
        self.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)

        # For dragging the frameless window
        self._offset_x = 0
        self._offset_y = 0

        # --- Main container ---
        self.main_container = ctk.CTkFrame(self, corner_radius=10)
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        self._build_title_bar()

        # --- Body and Buttons ---
        body_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        body_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        self.initial_focus = self.body(body_frame)

        self.buttonbox()

        # --- Modal Behavior ---
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        
        # Center on parent
        self.geometry(f"+{parent.winfo_rootx()+50}+{parent.winfo_rooty()+50}")

        if not self.initial_focus:
            self.initial_focus = self
        self.initial_focus.focus_set()
        
        self.wait_window(self)

    def _build_title_bar(self):
        title_bar = ctk.CTkFrame(self.main_container, corner_radius=0, height=35)
        title_bar.grid(row=0, column=0, sticky="ew")
        
        title_label = ctk.CTkLabel(title_bar, text=self.title_text, font=ctk.CTkFont(weight="bold"))
        title_label.pack(side="left", padx=15, pady=5)

        # Bind dragging events
        for widget in [title_bar, title_label]:
            widget.bind("<ButtonPress-1>", self._start_move)
            widget.bind("<ButtonRelease-1>", self._stop_move)
            widget.bind("<B1-Motion>", self._do_move)

    def body(self, master):
        """Override to create dialog body. Return widget that should have initial focus."""
        pass

    def buttonbox(self):
        box = ctk.CTkFrame(self.main_container, fg_color="transparent")
        box.grid(row=2, column=0, sticky="e", padx=15, pady=(0, 15))
        
        self.ok_button = ctk.CTkButton(box, text="OK", width=90, command=self.ok)
        self.ok_button.pack(side=tk.LEFT, padx=(0, 10))
        self.cancel_button = ctk.CTkButton(box, text="Cancel", width=90, command=self.cancel, fg_color="transparent", border_width=1)
        self.cancel_button.pack(side=tk.LEFT)
        
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

    def _start_move(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def _stop_move(self, event):
        self._offset_x = None
        self._offset_y = None

    def _do_move(self, event):
        if self._offset_x is not None and self._offset_y is not None:
            x = self.winfo_pointerx() - self._offset_x
            y = self.winfo_pointery() - self._offset_y
            self.geometry(f"+{x}+{y}")

    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set()
            return
        self.apply()
        self.result = True  # Indicate that the dialog was confirmed
        self.destroy()

    def cancel(self, event=None):
        self.result = None
        self.destroy()

    def validate(self):
        return True

    def apply(self):
        pass

class NewMappingDialog(BaseDialog):
    """Dialog for creating a new mapping file."""
    def __init__(self, parent, title):
        super().__init__(parent, title, geometry="450x260")

    def body(self, master):
        master.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(master, text="New Mapping Name:").grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.name_entry = ctk.CTkEntry(master)
        self.name_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self.import_var = tk.BooleanVar()
        self.import_check = ctk.CTkCheckBox(master, text="Import from existing mapping", variable=self.import_var, command=self.toggle_import)
        self.import_check.grid(row=2, column=0, sticky="w", pady=(10, 5))

        self.import_path_var = tk.StringVar()
        self.import_entry = ctk.CTkEntry(master, textvariable=self.import_path_var, state="disabled")
        self.import_entry.grid(row=3, column=0, sticky="ew")
        
        self.browse_btn = ctk.CTkButton(master, text="Browse...", command=self.browse_import, state="disabled")
        self.browse_btn.grid(row=4, column=0, sticky="e", pady=(5, 0))
        
        return self.name_entry

    def toggle_import(self):
        state = "normal" if self.import_var.get() else "disabled"
        self.import_entry.configure(state=state)
        self.browse_btn.configure(state=state)

    def browse_import(self):
        initial_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../mappings"))
        path = filedialog.askopenfilename(
            parent=self,
            title="Select Mapping File to Import",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=initial_dir
        )
        if path:
            self.import_path_var.set(path)

    def validate(self):
        self.mapping_name = self.name_entry.get().strip()
        if not self.mapping_name:
            messagebox.showerror("Invalid Name", "Mapping name cannot be empty.", parent=self)
            return False
        if self.import_var.get() and not self.import_path_var.get():
            messagebox.showerror("Invalid Path", "Please select a mapping file to import.", parent=self)
            return False
        return True

    def apply(self):
        self.import_selected = self.import_var.get()
        self.import_path = self.import_path_var.get() if self.import_selected else None

class PatternDestDialog(BaseDialog):
    """Dialog for adding or editing a mapping rule (phrase and destination)."""
    def __init__(self, parent, title, template_dir, destinations, initial_phrase="", initial_dest=""):
        self.template_dir = template_dir
        self.destinations = destinations
        self.initial_phrase = initial_phrase
        self.initial_dest = initial_dest
        super().__init__(parent, title, geometry="500x250")

    def body(self, master):
        master.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(master, text="Phrase/Keyword:").grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.phrase_entry = ctk.CTkEntry(master)
        self.phrase_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.phrase_entry.insert(0, self.initial_phrase)

        ctk.CTkLabel(master, text="Destination Folder:").grid(row=2, column=0, sticky="w", pady=(10, 2))
        self.dest_combo = ctk.CTkComboBox(master, values=self.destinations)
        self.dest_combo.grid(row=3, column=0, sticky="ew")
        if self.initial_dest in self.destinations:
            self.dest_combo.set(self.initial_dest)
        
        return self.phrase_entry

    def validate(self):
        self.phrase = self.phrase_entry.get().strip()
        self.dest = self.dest_combo.get().strip()
        if not self.phrase:
            messagebox.showerror("Invalid Phrase", "Phrase/Keyword cannot be empty.", parent=self)
            return False
        if not self.dest:
            messagebox.showerror("Invalid Destination", "Destination cannot be empty.", parent=self)
            return False
        return True

    def apply(self):
        # The result is read from the instance attributes after the dialog closes
        pass