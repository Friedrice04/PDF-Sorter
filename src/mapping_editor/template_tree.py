"""
TemplateTree widget for FileSorter.

This module provides the TemplateTree class, a ttk.Treeview-based widget for displaying
and managing the template directory structure. It supports:
- Selecting folders (with callback)
- Adding and deleting folders
- Drag-and-drop of folders from the OS (using tkinterdnd2), copying only the folder structure (no files)
- Refreshing the tree view

Dependencies:
- tkinterdnd2 (optional, for drag-and-drop support): pip install tkinterdnd2

"""

import os
import shutil
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    DND_FILES = None  # Drag-and-drop will be disabled if not installed

class TemplateTree(ttk.Treeview):
    """
    A tree widget for displaying and managing a template directory structure.

    Features:
    - Displays folders and subfolders in a tree view.
    - Allows selection of folders, with optional callback.
    - Allows adding and deleting folders.
    - Supports drag-and-drop of folders from the OS (copies only folder structure, not files).
    """

    def __init__(self, master, template_dir, on_folder_selected=None, **kwargs):
        """
        Initialize the TemplateTree.

        Args:
            master: Parent widget.
            template_dir (str): Path to the template directory.
            on_folder_selected (callable): Optional callback, called with relative path when a folder is selected.
            **kwargs: Additional arguments for ttk.Treeview.
        """
        super().__init__(master, **kwargs)
        self.template_dir = template_dir
        self.on_folder_selected = on_folder_selected

        self._populate_tree()
        self.bind("<<TreeviewSelect>>", self._on_select)

        # Enable drag-and-drop if tkinterdnd2 is available
        if DND_FILES:
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self._on_drop)

    def _populate_tree(self):
        """
        Populate the tree view with the current template directory structure.
        """
        # Save expanded state
        expanded = set()
        def save_expanded(item):
            if self.item(item, "open"):
                expanded.add(self.item(item, "values")[0])
            for child in self.get_children(item):
                save_expanded(child)
        for item in self.get_children():
            save_expanded(item)

        self.delete(*self.get_children())
        if not self.template_dir or not os.path.exists(self.template_dir):
            return

        def insert_nodes(parent, path):
            for name in sorted(os.listdir(path)):
                full_path = os.path.join(path, name)
                if os.path.isdir(full_path):
                    rel_path = os.path.relpath(full_path, self.template_dir)
                    node = self.insert(parent, "end", text=name, values=(rel_path,))
                    insert_nodes(node, full_path)
                    if rel_path in expanded:
                        self.item(node, open=True)
        insert_nodes("", self.template_dir)
        self.heading("#0", text=os.path.basename(self.template_dir))

    def _on_select(self, event):
        """
        Handle folder selection in the tree view.
        Calls the on_folder_selected callback if provided.
        """
        selected = self.selection()
        if selected and self.on_folder_selected:
            rel_path = self.item(selected[0], "values")[0]
            self.on_folder_selected(rel_path)

    def add_folder(self):
        """
        Prompt the user for a new folder name and add it to the selected folder or root.
        """
        selected = self.selection()
        parent_dir = self.template_dir
        parent_node = ''
        if selected:
            parent_node = selected[0]
            rel_path = self.item(parent_node, "values")[0]
            parent_dir = os.path.join(self.template_dir, rel_path)
        folder_name = simpledialog.askstring("New Folder", "Enter folder name:", parent=self)
        if folder_name:
            new_folder_path = os.path.join(parent_dir, folder_name)
            try:
                os.makedirs(new_folder_path, exist_ok=True)
                self._populate_tree()
                self._select_folder_by_path(os.path.relpath(new_folder_path, self.template_dir))
            except Exception as e:
                messagebox.showerror("Error", f"Could not create folder:\n{e}", parent=self)

    def delete_folder(self):
        """
        Delete the selected folder and all its contents after user confirmation.
        """
        selected = self.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a folder to delete.", parent=self)
            return
        node = selected[0]
        rel_path = self.item(node, "values")[0]
        abs_path = os.path.join(self.template_dir, rel_path)
        if not os.path.isdir(abs_path):
            messagebox.showerror("Error", "Selected path is not a folder.", parent=self)
            return
        if os.listdir(abs_path):
            if not messagebox.askyesno("Confirm Delete", "Folder is not empty. Delete anyway?", parent=self):
                return
        try:
            shutil.rmtree(abs_path)
            self._populate_tree()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete folder:\n{e}", parent=self)

    def _select_folder_by_path(self, rel_path):
        """
        Select a folder in the tree view by its relative path.

        Args:
            rel_path: Relative path from the template directory.
        """
        def search(node, target):
            for child in self.get_children(node):
                if self.item(child, "values")[0] == target:
                    self.selection_set(child)
                    self.see(child)
                    return True
                if search(child, target):
                    return True
            return False
        search('', rel_path)

    def _on_drop(self, event):
        """
        Handle drag-and-drop of folders from the OS.
        Only the folder structure (no files) is copied into the template directory.
        """
        paths = self.tk.splitlist(event.data)
        for path in paths:
            if os.path.isdir(path):
                self._copy_folder_structure_only(path, self.template_dir)
        self._populate_tree()
        messagebox.showinfo("Folders Added", "Folder structure added to template directory.")

    def _copy_folder_structure_only(self, src, dst):
        """
        Copy only the folder structure (no files) from src to dst/template_dir.

        Args:
            src: Source folder path.
            dst: Destination template directory.
        """
        for root, dirs, files in os.walk(src):
            rel_path = os.path.relpath(root, src)
            if rel_path == ".":
                target_dir = os.path.join(dst, os.path.basename(src))
            else:
                target_dir = os.path.join(dst, os.path.basename(src), rel_path)
            os.makedirs(target_dir, exist_ok=True)