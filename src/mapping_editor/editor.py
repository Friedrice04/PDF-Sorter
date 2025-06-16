import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import fnmatch
from collections import OrderedDict

from utils import (
    MappingUtils,
    show_error,
    ToolTip
)
from .pattern_builder import PatternBuilder

def labeled_entry(parent, label_text, var=None, **entry_kwargs):
    """
    Create a frame with a label and an entry.
    Returns (frame, entry).
    """
    frame = ttk.Frame(parent)
    label = ttk.Label(frame, text=label_text)
    label.pack(side="left")
    entry = ttk.Entry(frame, textvariable=var, **entry_kwargs)
    entry.pack(side="left", padx=5)
    return frame, entry

def button_with_tooltip(parent, text, command, tooltip_text):
    """
    Create a button with a tooltip.
    """
    btn = ttk.Button(parent, text=text, command=command)
    ToolTip(btn, tooltip_text)
    return btn

class MappingEditor(tk.Toplevel):
    """
    GUI window for creating and editing mapping files.
    Allows users to add, edit, delete, reorder, and test mapping entries.
    """
    def __init__(self, master, on_save_callback=None):
        super().__init__(master)
        self.title("Mapping Editor")
        self.geometry("600x400")
        self.on_save_callback = on_save_callback
        self.mapping = OrderedDict()
        self.mapping_path = None

        self._build_widgets()

    def _show_help(self):
        """
        Show a help dialog explaining the mapping editor and pattern matching.
        """
        message = (
            "Mapping Editor Help\n\n"
            "Use this window to create or edit mapping files.\n"
            "Each mapping entry consists of a pattern (wildcards allowed) and a destination folder.\n\n"
            "Pattern Matching:\n"
            "- Patterns use wildcards similar to Windows file searches:\n"
            "    *  matches any number of characters (e.g.,  *.pdf matches all PDF files)\n"
            "    ?  matches a single character (e.g.,  file?.txt matches file1.txt, fileA.txt)\n"
            "    [seq] matches any character in seq (e.g.,  file[12].txt matches file1.txt and file2.txt)\n"
            "- Patterns are matched against the filename only (not the full path).\n"
            "- The first pattern that matches a file will determine its destination folder.\n\n"
            "You can test patterns using the 'Test Pattern' section below the mapping table.\n"
            "Add, update, or delete entries, and save/load mapping files as needed."
        )
        messagebox.showinfo("Help - Mapping Editor", message)

    def _build_widgets(self):
        # --- Mapping file controls ---
        file_frame = ttk.Frame(self)
        file_frame.pack(fill="x", padx=10, pady=5)

        open_btn = button_with_tooltip(file_frame, "Open Mapping", self._open_mapping, "Open an existing mapping file.")
        open_btn.pack(side="left", padx=5)

        save_btn = button_with_tooltip(file_frame, "Save Mapping", self._save_mapping, "Save the current mapping to a file.")
        save_btn.pack(side="left", padx=5)

        new_btn = button_with_tooltip(file_frame, "New Mapping", self._new_mapping, "Start a new, empty mapping.")
        new_btn.pack(side="left", padx=5)

        # --- Mapping entries list with row numbers ---
        self.tree = ttk.Treeview(
            self,
            columns=("No", "Pattern", "Folder"),
            show="headings",
            selectmode="browse"
        )
        self.tree.heading("No", text="#")
        self.tree.heading("Pattern", text="Pattern")
        self.tree.heading("Folder", text="Destination Folder")
        self.tree.column("No", width=50, minwidth=30, anchor="center", stretch=False)
        self.tree.column("Pattern", width=200, stretch=True)
        self.tree.column("Folder", width=200, stretch=True)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<Double-1>", self._edit_entry)
        ToolTip(self.tree, "Double-click an entry to edit it.")

        # Enable drag and drop reordering (without interfering with selection)
        self.tree.bind("<ButtonPress-1>", self._on_tree_press)
        self.tree.bind("<B1-Motion>", self._on_tree_motion)
        self.tree.bind("<ButtonRelease-1>", self._on_tree_release)
        self._dragging_item = None
        self._drag_start_y = None
        self._drag_threshold = 5  # pixels
        self._dragging = False

        # --- Entry controls ---
        entry_frame = ttk.Frame(self)
        entry_frame.pack(fill="x", padx=10, pady=5)

        self.pattern_var = tk.StringVar()
        pattern_frame, self.pattern_entry = labeled_entry(entry_frame, "Pattern:", self.pattern_var, width=20)
        pattern_frame.pack(side="left")
        ToolTip(self.pattern_entry, "Enter a filename pattern (wildcards allowed).")

        pb_btn = button_with_tooltip(entry_frame, "Pattern Builder", self._open_pattern_builder, "Open a simple tool to build a pattern without wildcards.")
        pb_btn.pack(side="left", padx=5)

        self.folder_var = tk.StringVar()
        folder_frame, self.folder_entry = labeled_entry(entry_frame, "Folder:", self.folder_var, width=20)
        folder_frame.pack(side="left")
        ToolTip(self.folder_entry, "Enter the destination folder for this pattern.")

        add_btn = button_with_tooltip(entry_frame, "Add/Update", self._add_or_update_entry, "Add a new mapping entry or update the selected one.")
        add_btn.pack(side="left", padx=5)
        del_btn = button_with_tooltip(entry_frame, "Delete", self._delete_entry, "Delete the selected mapping entry.")
        del_btn.pack(side="left", padx=5)

        # --- Pattern test controls ---
        test_frame = ttk.Frame(self)
        test_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(test_frame, text="Test Filename:").pack(side="left")
        self.test_entry = ttk.Entry(test_frame, width=20)
        self.test_entry.pack(side="left", padx=5)
        ToolTip(self.test_entry, "Enter a filename to test against the pattern.")

        test_btn = button_with_tooltip(test_frame, "Test Pattern", self._test_pattern, "Test if the pattern matches the filename.")
        test_btn.pack(side="left", padx=5)

        self.test_result = ttk.Label(test_frame, text="")
        self.test_result.pack(side="left", padx=5)
        ToolTip(self.test_result, "Shows if the pattern matches the test filename.")

        # --- Help button in bottom right ---
        help_frame = ttk.Frame(self)
        help_frame.pack(fill="both", expand=False, padx=10, pady=5)
        help_btn = button_with_tooltip(help_frame, "Help", self._show_help, "Show help for the mapping editor.")
        help_btn.pack(side="right", anchor="se")

    def _refresh_tree(self):
        """
        Refresh the mapping entries displayed in the treeview, with row numbers.
        """
        self.tree.delete(*self.tree.get_children())
        for idx, (pattern, folder) in enumerate(self.mapping.items(), start=1):
            self.tree.insert("", "end", values=(idx, pattern, folder))

    def _open_mapping(self):
        folder = MappingUtils.get_mappings_folder()
        path = filedialog.askopenfilename(
            initialdir=folder,
            title="Open Mapping File",
            filetypes=[("JSON Files", "*.json")]
        )
        if path:
            try:
                self.mapping = OrderedDict(MappingUtils.load_json_file(path))
                self.mapping_path = path
                self._refresh_tree()
            except Exception as e:
                show_error(f"Failed to load mapping: {e}")

    def _save_mapping(self):
        if not MappingUtils.validate_mapping(self.mapping):
            show_error("Invalid mapping: Patterns and folders must be non-empty.")
            return
        if not self.mapping_path:
            folder = MappingUtils.get_mappings_folder()
            path = filedialog.asksaveasfilename(
                initialdir=folder,
                title="Save Mapping File",
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json")]
            )
            if not path:
                return
            self.mapping_path = path
        try:
            MappingUtils.save_json_file(self.mapping_path, dict(self.mapping))
            messagebox.showinfo("Saved", "Mapping saved successfully.")
            if self.on_save_callback:
                self.on_save_callback()
        except Exception as e:
            show_error(f"Failed to save mapping: {e}")

    def _new_mapping(self):
        self.mapping = OrderedDict()
        self.mapping_path = None
        self._refresh_tree()

    def _add_or_update_entry(self):
        pattern = self.pattern_entry.get().strip()
        folder = self.folder_entry.get().strip()
        if not pattern or not folder:
            show_error("Pattern and folder cannot be empty.")
            return

        selected = self.tree.selection()
        if selected:
            # Get the old pattern using the second column (Pattern)
            old_pattern = self.tree.item(selected[0])['values'][1]
            if old_pattern == pattern:
                self.mapping[pattern] = folder
            else:
                items = list(self.mapping.items())
                new_items = []
                for k, v in items:
                    if k == old_pattern:
                        new_items.append((pattern, folder))
                    else:
                        new_items.append((k, v))
                self.mapping = OrderedDict(new_items)
        else:
            self.mapping[pattern] = folder

        self._refresh_tree()
        self.pattern_entry.delete(0, tk.END)
        self.folder_entry.delete(0, tk.END)
        self.pattern_var.set("")
        self.folder_var.set("")

    def _delete_entry(self):
        selected = self.tree.selection()
        if not selected:
            return
        pattern = self.tree.item(selected[0])['values'][1]
        if pattern in self.mapping:
            del self.mapping[pattern]
            self._refresh_tree()

    def _edit_entry(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        _, pattern, folder = self.tree.item(selected[0])['values']
        self.pattern_entry.delete(0, tk.END)
        self.pattern_entry.insert(0, pattern)
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, folder)
        self.pattern_var.set(pattern)
        self.folder_var.set(folder)

    def _test_pattern(self):
        pattern = self.pattern_entry.get().strip()
        filename = self.test_entry.get().strip()
        if not pattern or not filename:
            self.test_result.config(text="Enter pattern and filename.")
            return
        if fnmatch.fnmatch(filename, pattern):
            self.test_result.config(text="MATCH", foreground="green")
        else:
            self.test_result.config(text="NO MATCH", foreground="red")

    def _open_pattern_builder(self):
        def set_pattern(pattern):
            self.pattern_entry.delete(0, tk.END)
            self.pattern_entry.insert(0, pattern)
            self.pattern_var.set(pattern)
        PatternBuilder(self, set_pattern)

    # Drag and drop reordering (with selection preserved)
    def _on_tree_press(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self._dragging_item = item
            self._drag_start_y = event.y
            self._dragging = False
        else:
            self._dragging_item = None
            self._drag_start_y = None
            self._dragging = False

    def _on_tree_motion(self, event):
        if not self._dragging_item or self._drag_start_y is None:
            return
        if not self._dragging and abs(event.y - self._drag_start_y) < self._drag_threshold:
            return
        self._dragging = True
        target = self.tree.identify_row(event.y)
        if target and target != self._dragging_item:
            idx_drag = self.tree.index(self._dragging_item)
            idx_target = self.tree.index(target)
            self.tree.move(self._dragging_item, '', idx_target)
            self._dragging_item = self.tree.get_children()[idx_target]
            self._drag_start_y = event.y

    def _on_tree_release(self, event):
        if self._dragging_item is None or not self._dragging:
            self._dragging_item = None
            self._drag_start_y = None
            self._dragging = False
            return
        new_order = []
        for item in self.tree.get_children():
            _, pattern, folder = self.tree.item(item)['values']
            new_order.append((pattern, folder))
        self.mapping = OrderedDict(new_order)
        self._refresh_tree()
        self._dragging_item = None
        self._drag_start_y = None
        self._dragging = False