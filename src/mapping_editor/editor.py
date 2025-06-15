import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import fnmatch
from collections import OrderedDict

from utils import (
    get_mappings_folder,
    show_error,
    validate_mapping,
    save_json_file,
    load_json_file,
)
from .tooltip import ToolTip
from .pattern_builder import PatternBuilder

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
        # Mapping file controls
        file_frame = ttk.Frame(self)
        file_frame.pack(fill="x", padx=10, pady=5)

        open_btn = ttk.Button(file_frame, text="Open Mapping", command=self._open_mapping)
        open_btn.pack(side="left", padx=5)
        ToolTip(open_btn, "Open an existing mapping file.")

        save_btn = ttk.Button(file_frame, text="Save Mapping", command=self._save_mapping)
        save_btn.pack(side="left", padx=5)
        ToolTip(save_btn, "Save the current mapping to a file.")

        new_btn = ttk.Button(file_frame, text="New Mapping", command=self._new_mapping)
        new_btn.pack(side="left", padx=5)
        ToolTip(new_btn, "Start a new, empty mapping.")

        # Mapping entries list with row numbers
        self.tree = ttk.Treeview(
            self,
            columns=("No", "Pattern", "Folder"),
            show="headings",
            selectmode="browse"
        )
        self.tree.heading("No", text="#")
        self.tree.heading("Pattern", text="Pattern")
        self.tree.heading("Folder", text="Destination Folder")
        self.tree.column("No", width=50, minwidth=30, anchor="center")  # Set default width here
        self.tree.column("Pattern", width=200)
        self.tree.column("Folder", width=200)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<Double-1>", self._edit_entry)
        ToolTip(self.tree, "Double-click an entry to edit it.")

        # Enable drag and drop reordering
        self.tree.bind("<ButtonPress-1>", self._on_tree_press)
        self.tree.bind("<B1-Motion>", self._on_tree_motion)
        self.tree.bind("<ButtonRelease-1>", self._on_tree_release)
        self._dragging_item = None

        # Entry controls
        entry_frame = ttk.Frame(self)
        entry_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(entry_frame, text="Pattern:").pack(side="left")
        self.pattern_entry = ttk.Entry(entry_frame, width=20)
        self.pattern_entry.pack(side="left", padx=5)
        ToolTip(self.pattern_entry, "Enter a filename pattern (wildcards allowed).")

        pb_btn = ttk.Button(entry_frame, text="Pattern Builder", command=self._open_pattern_builder)
        pb_btn.pack(side="left", padx=5)
        ToolTip(pb_btn, "Open a simple tool to build a pattern without wildcards.")

        ttk.Label(entry_frame, text="Folder:").pack(side="left")
        self.folder_entry = ttk.Entry(entry_frame, width=20)
        self.folder_entry.pack(side="left", padx=5)
        ToolTip(self.folder_entry, "Enter the destination folder for this pattern.")

        add_btn = ttk.Button(entry_frame, text="Add/Update", command=self._add_or_update_entry)
        add_btn.pack(side="left", padx=5)
        ToolTip(add_btn, "Add a new mapping entry or update the selected one.")

        del_btn = ttk.Button(entry_frame, text="Delete", command=self._delete_entry)
        del_btn.pack(side="left", padx=5)
        ToolTip(del_btn, "Delete the selected mapping entry.")

        # Pattern test controls
        test_frame = ttk.Frame(self)
        test_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(test_frame, text="Test Filename:").pack(side="left")
        self.test_entry = ttk.Entry(test_frame, width=20)
        self.test_entry.pack(side="left", padx=5)
        ToolTip(self.test_entry, "Enter a filename to test against the pattern.")

        test_btn = ttk.Button(test_frame, text="Test Pattern", command=self._test_pattern)
        test_btn.pack(side="left", padx=5)
        ToolTip(test_btn, "Test if the pattern matches the filename.")

        self.test_result = ttk.Label(test_frame, text="")
        self.test_result.pack(side="left", padx=5)
        ToolTip(self.test_result, "Shows if the pattern matches the test filename.")

        # Help button in bottom right
        help_frame = ttk.Frame(self)
        help_frame.pack(fill="both", expand=False, padx=10, pady=5)
        help_btn = ttk.Button(help_frame, text="Help", command=self._show_help)
        help_btn.pack(side="right", anchor="se")
        ToolTip(help_btn, "Show help for the mapping editor.")

    def _refresh_tree(self):
        """
        Refresh the mapping entries displayed in the treeview, with row numbers.
        """
        self.tree.delete(*self.tree.get_children())
        for idx, (pattern, folder) in enumerate(self.mapping.items(), start=1):
            self.tree.insert("", "end", values=(idx, pattern, folder))

    def _open_mapping(self):
        folder = get_mappings_folder()
        path = filedialog.askopenfilename(
            initialdir=folder,
            title="Open Mapping File",
            filetypes=[("JSON Files", "*.json")]
        )
        if path:
            try:
                self.mapping = OrderedDict(load_json_file(path))
                self.mapping_path = path
                self._refresh_tree()
            except Exception as e:
                show_error(f"Failed to load mapping: {e}")

    def _save_mapping(self):
        if not validate_mapping(self.mapping):
            show_error("Invalid mapping: Patterns and folders must be non-empty.")
            return
        if not self.mapping_path:
            folder = get_mappings_folder()
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
            save_json_file(self.mapping_path, dict(self.mapping))
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
        """
        Add a new mapping entry or update the selected one, preserving order.
        """
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

    def _delete_entry(self):
        selected = self.tree.selection()
        if not selected:
            return
        # Use the second column (Pattern) for the key
        pattern = self.tree.item(selected[0])['values'][1]
        if pattern in self.mapping:
            del self.mapping[pattern]
            self._refresh_tree()

    def _edit_entry(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        # Use the second and third columns for pattern and folder
        _, pattern, folder = self.tree.item(selected[0])['values']
        self.pattern_entry.delete(0, tk.END)
        self.pattern_entry.insert(0, pattern)
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, folder)

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
        PatternBuilder(self, set_pattern)

    # Drag and drop reordering
    def _on_tree_press(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self._dragging_item = item
        else:
            self._dragging_item = None

    def _on_tree_motion(self, event):
        if not self._dragging_item:
            return
        target = self.tree.identify_row(event.y)
        if target and target != self._dragging_item:
            idx_drag = self.tree.index(self._dragging_item)
            idx_target = self.tree.index(target)
            self.tree.move(self._dragging_item, '', idx_target)
            self._dragging_item = self.tree.get_children()[idx_target]

    def _on_tree_release(self, event):
        if self._dragging_item is None:
            return
        new_order = []
        for item in self.tree.get_children():
            # Use the second and third columns for pattern and folder
            _, pattern, folder = self.tree.item(item)['values']
            new_order.append((pattern, folder))
        self.mapping = OrderedDict(new_order)
        self._refresh_tree()
        self._dragging_item