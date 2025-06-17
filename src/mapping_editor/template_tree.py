import os
import shutil
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

class TemplateTree(ttk.Treeview):
    """
    Custom Treeview for displaying and managing the template directory structure.
    Supports context menu for add/delete and can be expanded for drag-and-drop.
    """
    def __init__(self, master, template_dir, on_folder_selected=None, **kwargs):
        super().__init__(master, **kwargs)
        self.template_dir = template_dir
        self.on_folder_selected = on_folder_selected
        self._build_context_menu()
        self.bind("<Button-3>", self._on_right_click)
        self.bind("<<TreeviewSelect>>", self._on_select)
        self.heading("#0", text=os.path.basename(self.template_dir) if self.template_dir else "Template")
        self._populate_tree()

    def _populate_tree(self):
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

    def _build_context_menu(self):
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="New Folder", command=self._context_add_folder)
        self.menu.add_command(label="Delete Folder", command=self._context_delete_folder)

    def _on_right_click(self, event):
        item = self.identify_row(event.y)
        if item:
            self.selection_set(item)
            self.menu.entryconfig("Delete Folder", state="normal")
            self.menu.tk_popup(event.x_root, event.y_root)
        else:
            self.selection_remove(self.selection())
            self.menu.entryconfig("Delete Folder", state="disabled")
            self.menu.tk_popup(event.x_root, event.y_root)
            self.menu.entryconfig("Delete Folder", state="normal")

    def _context_add_folder(self):
        self.add_folder()

    def _context_delete_folder(self):
        self.delete_folder()

    def add_folder(self):
        selected = self.selection()
        if selected:
            parent_rel_path = self.item(selected[0], "values")[0]
            parent_path = os.path.join(self.template_dir, parent_rel_path)
        else:
            parent_path = self.template_dir
        folder_name = simpledialog.askstring("New Folder", "Enter folder name:", parent=self)
        if folder_name:
            new_folder_path = os.path.join(parent_path, folder_name)
            try:
                os.makedirs(new_folder_path, exist_ok=True)
                self._populate_tree()
            except Exception as e:
                messagebox.showerror("Error", f"Could not create folder:\n{e}", parent=self)

    def delete_folder(self):
        selected = self.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a folder to delete.", parent=self)
            return
        rel_path = self.item(selected[0], "values")[0]
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

    def _on_select(self, event):
        if self.on_folder_selected:
            selected = self.selection()
            if selected:
                rel_path = self.item(selected[0], "values")[0]
                self.on_folder_selected(rel_path)
            else:
                self.on_folder_selected(None)