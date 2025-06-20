import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from .dialogs import NewMappingDialog, PatternDestDialog
from src import utils

MAPPINGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../mappings"))

class EditorActions:
    """
    Handles user actions and coordinates between the View (Editor) and Model (Logic).
    """
    def __init__(self, view, logic):
        self.view = view
        self.logic = logic
        self._dragged_item = None
        self._dragging = False

    def on_close_window(self):
        """Handle closing the window, checking for unsaved changes."""
        if self._check_unsaved_changes():
            self.view.destroy()

    def on_mapping_file_selected(self, event=None):
        """Load a new mapping file when selected from the combobox."""
        if not self._check_unsaved_changes():
            self.view.update_mapping_file_display(self.logic.mapping_path)
            return
        selected_file = self.view.mapping_file_var.get()
        if not selected_file: return
        
        file_path = os.path.join(MAPPINGS_DIR, selected_file)
        self.logic.load_mapping_file(file_path)
        self.view.refresh_all()

    def on_new_mapping(self):
        """Handle the 'New Mapping' button click."""
        if not self._check_unsaved_changes(): return
        
        dialog = NewMappingDialog(self.view, "New Mapping")
        if not dialog.mapping_name: return

        mapping_path = os.path.join(MAPPINGS_DIR, dialog.mapping_name + ".json")
        if os.path.exists(mapping_path):
            messagebox.showerror("File Exists", "A mapping file with that name already exists.", parent=self.view)
            return

        template_dir = self.logic._get_template_dir(mapping_path)
        os.makedirs(template_dir, exist_ok=True)

        if dialog.import_selected and dialog.import_path:
            import shutil
            shutil.copy(dialog.import_path, mapping_path)
            import_template_dir = self.logic._get_template_dir(dialog.import_path)
            if os.path.exists(import_template_dir):
                if os.path.exists(template_dir): shutil.rmtree(template_dir)
                shutil.copytree(import_template_dir, template_dir)
        else:
            with open(mapping_path, "w", encoding="utf-8") as f: f.write("{}")
        
        self.logic.load_mapping_file(mapping_path)
        self.view.refresh_all(reload_files=True)

    def on_save(self):
        """Handle the 'Save' button click."""
        success, message = self.logic.save_mappings()
        if success:
            self.view.set_dirty(False)
            if self.view.on_save_callback:
                self.view.on_save_callback()
            messagebox.showinfo("Saved", message, parent=self.view)
        else:
            messagebox.showerror("Error", message, parent=self.view)

    def on_add_rule(self):
        """Handle adding a new mapping rule."""
        destinations = self._get_all_destinations()
        dialog = PatternDestDialog(self.view, "Add Rule", self.logic.template_dir, destinations)
        if not dialog.phrase or not dialog.dest: return

        success, message = self.logic.add_rule(dialog.phrase, dialog.dest)
        if success:
            self.view.refresh_mapping_table()
            self.view.set_dirty(True)
        else:
            messagebox.showwarning("Warning", message, parent=self.view)

    def on_edit_rule(self):
        """Handle editing an existing mapping rule."""
        selected_item = self.view.mapping_table.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a mapping to edit.", parent=self.view)
            return
        
        phrase, dest = self.view.mapping_table.item(selected_item[0], "values")
        destinations = self._get_all_destinations()
        dialog = PatternDestDialog(self.view, "Edit Rule", self.logic.template_dir, destinations, initial_phrase=phrase, initial_dest=dest)
        if not dialog.phrase or not dialog.dest: return

        success, message = self.logic.update_rule(phrase, dialog.phrase, dialog.dest)
        if success:
            self.view.refresh_mapping_table()
            self.view.set_dirty(True)
        else:
            messagebox.showwarning("Warning", message, parent=self.view)

    def on_remove_rule(self):
        """Handle removing a mapping rule."""
        selected_item = self.view.mapping_table.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a mapping to remove.", parent=self.view)
            return
        phrase, _ = self.view.mapping_table.item(selected_item[0], "values")
        self.logic.remove_rule(phrase)
        self.view.refresh_mapping_table()
        self.view.set_dirty(True)

    def on_move_rule(self, direction):
        """Handle moving a rule up or down."""
        selected_item = self.view.mapping_table.selection()
        if not selected_item: return
        phrase, _ = self.view.mapping_table.item(selected_item[0], "values")
        if self.logic.move_rule(phrase, direction):
            self.view.refresh_mapping_table()
            # Reselect the item after refresh
            new_index = list(self.logic.mappings.keys()).index(phrase)
            self.view.mapping_table.selection_set(self.view.mapping_table.get_children()[new_index])
            self.view.set_dirty(True)

    def on_rename_template_folder(self):
        """Handle renaming a folder in the template tree."""
        selected_item = self.view.template_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a folder to rename.", parent=self.view)
            return
        
        old_rel_path = self.view.template_tree.item(selected_item[0], "values")[0]
        old_name = os.path.basename(old_rel_path)
        new_name = simpledialog.askstring("Rename Folder", f"Enter new name for '{old_name}':", parent=self.view)
        if not new_name or new_name == old_name: return

        success, message = self.logic.rename_template_folder(old_rel_path, new_name)
        if success:
            self.view.refresh_all()
            self.view.set_dirty(True)
        else:
            messagebox.showerror("Error", message, parent=self.view)

    def on_autobuild_tree(self):
        """Handle the 'Auto-Build Tree' button click."""
        created = self.logic.autobuild_template_tree()
        self.view.refresh_template_tree()
        messagebox.showinfo("Done", f"Template tree updated. Folders created/ensured: {created}", parent=self.view)

    def on_drag_release(self, event):
        """Handle the release of a drag-and-drop operation."""
        if not self._dragging or not self._dragged_item: return
        
        widget = self.view.winfo_containing(self.view.winfo_pointerx(), self.view.winfo_pointery())
        if widget == self.view.template_tree:
            y = self.view.template_tree.winfo_pointery() - self.view.template_tree.winfo_rooty()
            dest_item = self.view.template_tree.identify_row(y)
            rel_path = self.view.template_tree.item(dest_item, "values")[0] if dest_item else "."
            
            if self.logic.mappings[self._dragged_item] != rel_path:
                self.logic.mappings[self._dragged_item] = rel_path
                self.view.refresh_mapping_table()
                self.view.set_dirty(True)
        
        self._dragging = False
        self._dragged_item = None

    def on_item_drag_start(self, item):
        self._dragged_item = item
        self._dragging = True

    def _check_unsaved_changes(self):
        """Check for unsaved changes and prompt user. Return True if it's safe to proceed."""
        if not self.logic.is_dirty: return True
        response = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save them?", parent=self.view)
        if response is True: # Yes
            self.on_save()
            return not self.logic.is_dirty
        elif response is False: # No
            return True
        else: # Cancel
            return False

    def _get_all_destinations(self):
        """Get all possible destination folders from the template directory."""
        destinations = []
        if self.logic.template_dir and os.path.exists(self.logic.template_dir):
            for root, dirs, _ in os.walk(self.logic.template_dir):
                for d in sorted(dirs):
                    full_path = os.path.join(root, d)
                    rel_path = os.path.relpath(full_path, self.logic.template_dir)
                    destinations.append(rel_path)
            destinations.sort()
            destinations.insert(0, ".")
        return destinations
