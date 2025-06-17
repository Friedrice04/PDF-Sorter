import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from .dialogs import NewMappingDialog, PatternDestDialog
from .template_tree import TemplateTree
from .mapping_table import MappingTable
from src.utils import ToolTip
from src import utils

class MappingEditor(tk.Toplevel):
    """
    Main window for editing file sorting mappings, using MappingTable and TemplateTree.
    Supports drag-and-drop from the mapping table to the template tree to set destinations.
    """
    def __init__(self, master, on_save_callback=None, mapping_path=None):
        super().__init__(master)
        self.title("Mapping Editor")
        self.geometry("1000x600")
        self.on_save_callback = on_save_callback
        self.mappings = {}  # pattern: destination
        self.mapping_path = mapping_path
        self.template_dir = None

        self._dragged_pattern = None
        self._dragging = False
        self._drag_context = None

        self._build_widgets()
        # Bind global mouse release for drag-and-drop (only for setting destination)
        self.bind_all("<ButtonRelease-1>", self._on_drag_release)

        if self.mapping_path:
            self.mapping_file_var.set(os.path.basename(self.mapping_path))
            self.template_dir = self._get_template_dir(self.mapping_path)
            if not os.path.exists(self.template_dir):
                os.makedirs(self.template_dir)
            self._load_mappings()
            self._populate_template_tree()

    def _build_widgets(self):
        # --- Mapping file selection ---
        file_frame = ttk.Frame(self)
        file_frame.pack(fill="x", padx=10, pady=(10, 0))

        self.mapping_file_var = tk.StringVar()
        file_label = ttk.Label(
            file_frame,
            textvariable=self.mapping_file_var,
            font=("Segoe UI", 11, "bold"),
            foreground="#2a4d7f",
            background="#f0f4fa",
            anchor="w"
        )
        file_label.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=2, ipadx=4)
        ToolTip(file_label, "Currently selected mapping JSON file.")

        select_btn = ttk.Button(file_frame, text="Select Mapping File...", command=self._select_mapping_file)
        select_btn.pack(side="left")
        ToolTip(select_btn, "Choose a mapping JSON file to edit.")

        new_btn = ttk.Button(file_frame, text="New Mapping", command=self._new_mapping_file)
        new_btn.pack(side="left", padx=(5, 0))
        ToolTip(new_btn, "Create a new mapping file and associated template directory.")

        # --- Main PanedWindow for resizable split view ---
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Left: Mapping rules table and buttons ---
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=3)

        mapping_label = ttk.Label(left_frame, text="Pattern → Destination", font=("Segoe UI", 10, "bold"))
        mapping_label.pack(anchor="w", padx=5, pady=(0, 2))

        self.mapping_table = MappingTable(left_frame, on_pattern_drag=self._on_pattern_drag_event)
        self.mapping_table.pack(fill="both", expand=True, padx=0, pady=0)
        ToolTip(self.mapping_table, "Patterns and their destination folders.")

        # Enable drag-and-drop ONLY for setting destination (not for reordering)
        self.mapping_table.bind("<Motion>", self._on_drag_motion_context)
        self.template_tree = None  # Will be set below

        # Double-click to edit
        self.mapping_table.bind("<Double-Button-1>", lambda e: self._edit_rule())

        # Right-click context menu for add/remove/edit
        self._build_mapping_table_menu()
        self.mapping_table.bind("<Button-3>", self._on_mapping_table_right_click)

        # Button frame below the list
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill="x", pady=(8, 0))

        add_btn = ttk.Button(button_frame, text="Add", command=self._add_rule)
        add_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ToolTip(add_btn, "Add a new pattern mapping.")

        remove_btn = ttk.Button(button_frame, text="Remove", command=self._remove_rule)
        remove_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ToolTip(remove_btn, "Remove the selected mapping.")

        move_up_btn = ttk.Button(button_frame, text="Move Up", command=self._move_up)
        move_up_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ToolTip(move_up_btn, "Move the selected mapping up.")

        move_down_btn = ttk.Button(button_frame, text="Move Down", command=self._move_down)
        move_down_btn.pack(side="left", fill="x", expand=True)
        ToolTip(move_down_btn, "Move the selected mapping down.")

        # --- Right: Template directory treeview and controls ---
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)

        template_label = ttk.Label(right_frame, text="Template Directory Structure", font=("Segoe UI", 10, "bold"))
        template_label.pack(anchor="w", padx=5, pady=(0, 2))

        self.template_tree = TemplateTree(
            right_frame,
            self.template_dir,
            on_folder_selected=self._on_folder_selected
        )
        self.template_tree.pack(fill="both", expand=True, padx=(0, 5), pady=0)
        ToolTip(self.template_tree, "Visualize and manage the template directory structure.")

        # Add right-click context menu for template tree
        self._build_template_tree_menu()
        self.template_tree.bind("<Button-3>", self._on_template_tree_right_click)

        # Template folder controls below the tree
        template_btn_frame = ttk.Frame(right_frame)
        template_btn_frame.pack(fill="x", pady=(8, 0))

        add_template_folder_btn = ttk.Button(template_btn_frame, text="New Folder", command=self._add_folder_to_template)
        add_template_folder_btn.pack(side="left", padx=(0, 5))
        ToolTip(add_template_folder_btn, "Create a new folder in the template directory.")

        del_template_folder_btn = ttk.Button(template_btn_frame, text="Delete Folder", command=self._delete_folder_from_template)
        del_template_folder_btn.pack(side="left", padx=(0, 5))
        ToolTip(del_template_folder_btn, "Delete the selected folder from the template directory.")

        refresh_template_btn = ttk.Button(template_btn_frame, text="Refresh", command=self._populate_template_tree)
        refresh_template_btn.pack(side="left")
        ToolTip(refresh_template_btn, "Refresh the template directory view.")

        # --- Save and Cancel at the bottom ---
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", padx=10, pady=(0, 10))

        save_btn = ttk.Button(bottom_frame, text="Save", command=self._save)
        save_btn.pack(side="right", padx=(5, 0))
        ToolTip(save_btn, "Save changes to the mapping file.")

        cancel_btn = ttk.Button(bottom_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side="right")
        ToolTip(cancel_btn, "Cancel and close the editor.")

    def _build_mapping_table_menu(self):
        self.mapping_table_menu = tk.Menu(self, tearoff=0)
        self.mapping_table_menu.add_command(label="Add Pattern", command=self._add_rule)
        self.mapping_table_menu.add_command(label="Edit Pattern", command=self._edit_rule)
        self.mapping_table_menu.add_command(label="Remove Pattern", command=self._remove_rule)

    def _on_mapping_table_right_click(self, event):
        item = self.mapping_table.identify_row(event.y)
        if item:
            self.mapping_table.selection_set(item)
            self.mapping_table_menu.entryconfig("Edit Pattern", state="normal")
            self.mapping_table_menu.entryconfig("Remove Pattern", state="normal")
        else:
            self.mapping_table.selection_remove(self.mapping_table.selection())
            self.mapping_table_menu.entryconfig("Edit Pattern", state="disabled")
            self.mapping_table_menu.entryconfig("Remove Pattern", state="disabled")
        self.mapping_table_menu.tk_popup(event.x_root, event.y_root)

    def _build_template_tree_menu(self):
        self.template_tree_menu = tk.Menu(self, tearoff=0)
        self.template_tree_menu.add_command(label="Add Folder", command=self._add_folder_to_template)
        self.template_tree_menu.add_command(label="Rename Folder", command=self._rename_folder_in_template)
        self.template_tree_menu.add_command(label="Delete Folder", command=self._delete_folder_from_template)

    def _on_template_tree_right_click(self, event):
        item = self.template_tree.identify_row(event.y)
        if item:
            self.template_tree.selection_set(item)
            self.template_tree_menu.entryconfig("Rename Folder", state="normal")
            self.template_tree_menu.entryconfig("Delete Folder", state="normal")
        else:
            self.template_tree.selection_remove(self.template_tree.selection())
            self.template_tree_menu.entryconfig("Rename Folder", state="disabled")
            self.template_tree_menu.entryconfig("Delete Folder", state="disabled")
        self.template_tree_menu.tk_popup(event.x_root, event.y_root)

    def _rename_folder_in_template(self):
        selected = self.template_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a folder to rename.")
            return
        item = selected[0]
        old_rel_path = self.template_tree.item(item, "values")[0]
        old_abs_path = os.path.join(self.template_dir, old_rel_path)
        old_folder_name = os.path.basename(old_rel_path)

        # Prompt for new folder name
        new_folder_name = simpledialog.askstring("Rename Folder", f"Enter new name for folder '{old_folder_name}':", parent=self)
        if not new_folder_name or new_folder_name == old_folder_name:
            return

        new_rel_path = os.path.join(os.path.dirname(old_rel_path), new_folder_name)
        new_abs_path = os.path.join(self.template_dir, new_rel_path)

        # Check if new folder already exists
        if os.path.exists(new_abs_path):
            messagebox.showerror("Folder Exists", "A folder with that name already exists.", parent=self)
            return

        try:
            os.rename(old_abs_path, new_abs_path)
        except Exception as e:
            messagebox.showerror("Rename Failed", f"Could not rename folder:\n{e}", parent=self)
            return

        # Update all mappings whose destination includes the old folder path
        updated_mappings = {}
        for pattern, dest in self.mappings.items():
            # If dest is "." or empty, skip
            if not dest or dest == ".":
                updated_mappings[pattern] = dest
                continue
            # Normalize paths for comparison
            norm_dest = os.path.normpath(dest)
            norm_old = os.path.normpath(old_rel_path)
            if norm_dest == norm_old or norm_dest.startswith(norm_old + os.sep):
                # Replace only the first occurrence
                new_dest = os.path.normpath(
                    norm_dest.replace(norm_old, new_rel_path, 1)
                )
                updated_mappings[pattern] = new_dest
            else:
                updated_mappings[pattern] = dest
        self.mappings = updated_mappings
        self._refresh_mapping_table()
        self._populate_template_tree()

    def _get_template_dir(self, mapping_path):
        base, _ = os.path.splitext(mapping_path)
        return base + "_template"

    def _select_mapping_file(self):
        mappings_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../mappings"))
        os.makedirs(mappings_folder, exist_ok=True)

        json_files = [f for f in os.listdir(mappings_folder) if f.endswith(".json")]
        if not json_files:
            messagebox.showinfo("No Mappings", "No mapping JSON files found in the mappings folder.", parent=self)
            return

        dialog = tk.Toplevel(self)
        dialog.title("Select Mapping File")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        label = ttk.Label(dialog, text="Double-click a mapping file to select:")
        label.pack(padx=10, pady=(10, 5), anchor="w")

        listbox = tk.Listbox(dialog, height=15)
        for f in json_files:
            listbox.insert(tk.END, f)
        listbox.pack(fill="both", expand=True, padx=10, pady=5)

        selected_file = {"name": None}

        def on_select(event=None):
            selection = listbox.curselection()
            if selection:
                selected_file["name"] = listbox.get(selection[0])
                dialog.destroy()

        listbox.bind("<Double-Button-1>", on_select)

        def on_cancel():
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=on_cancel)
        cancel_btn.pack(side="right")

        dialog.wait_window()

        if selected_file["name"]:
            file_path = os.path.join(mappings_folder, selected_file["name"])
            self.mapping_path = file_path
            self.mapping_file_var.set(os.path.basename(file_path))
            self.template_dir = self._get_template_dir(file_path)
            if not os.path.exists(self.template_dir):
                os.makedirs(self.template_dir)
            self._load_mappings()
            self._populate_template_tree()

    def _new_mapping_file(self):
        mappings_folder = os.path.join(os.path.dirname(__file__), "../mappings")
        mappings_folder = os.path.abspath(mappings_folder)
        os.makedirs(mappings_folder, exist_ok=True)
        dialog = NewMappingDialog(self, "New Mapping")
        mapping_name = getattr(dialog, "mapping_name", None)
        import_selected = getattr(dialog, "import_selected", False)
        import_path = getattr(dialog, "import_path", None)
        if not mapping_name:
            return
        mapping_path = os.path.join(mappings_folder, mapping_name + ".json")
        if os.path.exists(mapping_path):
            messagebox.showerror("File Exists", "A mapping file with that name already exists.", parent=self)
            return
        template_dir = self._get_template_dir(mapping_path)
        os.makedirs(template_dir, exist_ok=True)
        if import_selected and import_path:
            import shutil
            shutil.copy(import_path, mapping_path)
            import_template_dir = self._get_template_dir(import_path)
            if os.path.exists(import_template_dir):
                dest_template_dir = template_dir
                if os.path.exists(dest_template_dir):
                    shutil.rmtree(dest_template_dir)
                shutil.copytree(import_template_dir, dest_template_dir)
        else:
            with open(mapping_path, "w", encoding="utf-8") as f:
                f.write("{}")
        self.mapping_path = mapping_path
        self.mapping_file_var.set(os.path.basename(mapping_path))
        self.template_dir = template_dir
        self.mappings = {}
        self._refresh_mapping_table()
        self._populate_template_tree()
        if import_selected and import_path:
            self._load_mappings()

    def _load_mappings(self):
        if self.mapping_path and utils.MappingUtils.is_valid_mapping_file(self.mapping_path):
            self.mappings = utils.MappingUtils.load_mapping(self.mapping_path)
            self._refresh_mapping_table()
        else:
            self.mappings = {}
            self.mapping_table.delete(*self.mapping_table.get_children())

    def _refresh_mapping_table(self):
        self.mapping_table.refresh(self.mappings)

    def _get_all_destinations(self):
        destinations = []
        if self.template_dir and os.path.exists(self.template_dir):
            for root, dirs, _ in os.walk(self.template_dir):
                for d in dirs:
                    full_path = os.path.join(root, d)
                    rel_path = os.path.relpath(full_path, self.template_dir)
                    destinations.append(rel_path)
            destinations.insert(0, ".")
        return destinations

    def _populate_template_tree(self):
        self.template_tree.template_dir = self.template_dir
        self.template_tree._populate_tree()

    def _add_folder_to_template(self):
        self.template_tree.add_folder()

    def _delete_folder_from_template(self):
        self.template_tree.delete_folder()

    def _on_folder_selected(self, rel_path):
        pass

    # --- Drag and drop logic for assigning destination folders ---

    def _on_pattern_drag_event(self, action, pattern, event=None):
        if action == "start":
            self._dragged_pattern = pattern
            self._dragging = True
        elif action == "motion":
            if self._dragging:
                self._highlight_template_tree_under_pointer()

    def _on_drag_motion_context(self, event):
        if self._dragging and self._dragged_pattern:
            widget = event.widget
            if widget == self.template_tree:
                self._drag_context = "template"
                self._highlight_template_tree_under_pointer()
            else:
                self._drag_context = None

    def _on_drag_release(self, event):
        if not self._dragging or not self._dragged_pattern:
            return

        widget = self.winfo_containing(self.winfo_pointerx(), self.winfo_pointery())
        if widget == self.template_tree:
            self._clear_template_tree_highlight()
            x = self.template_tree.winfo_pointerx() - self.template_tree.winfo_rootx()
            y = self.template_tree.winfo_pointery() - self.template_tree.winfo_rooty()
            dest_item = self.template_tree.identify_row(y)
            if dest_item:
                rel_path = self.template_tree.item(dest_item, "values")[0]
                self._highlight_drop_target(dest_item)
            else:
                rel_path = "."
            if self._dragged_pattern in self.mappings:
                self.mappings[self._dragged_pattern] = rel_path
                self._refresh_mapping_table()

        # Reset drag state
        self._dragged_pattern = None
        self._dragging = False
        self._drag_context = None

    def _highlight_template_tree_under_pointer(self):
        self._clear_template_tree_highlight()
        x = self.template_tree.winfo_pointerx() - self.template_tree.winfo_rootx()
        y = self.template_tree.winfo_pointery() - self.template_tree.winfo_rooty()
        item = self.template_tree.identify_row(y)
        if item:
            self.template_tree.tag_configure("drag_highlight", background="#a1e3f7")
            self.template_tree.item(item, tags=("drag_highlight",))
            self._last_highlighted_item = item
        else:
            self._last_highlighted_item = None

    def _clear_template_tree_highlight(self):
        for item in self.template_tree.get_children(""):
            self._clear_highlight_recursive(item)

    def _clear_highlight_recursive(self, item):
        self.template_tree.item(item, tags=())
        for child in self.template_tree.get_children(item):
            self._clear_highlight_recursive(child)

    def _highlight_drop_target(self, item):
        self.template_tree.tag_configure("drop_highlight", background="#7fe3a1")
        self.template_tree.item(item, tags=("drop_highlight",))
        self.after(350, lambda: self.template_tree.item(item, tags=()))

    # --- End drag and drop logic ---

    def _add_rule(self):
        if not self.template_dir or not os.path.exists(self.template_dir):
            messagebox.showerror("No Template Directory", "Please select a mapping file first.", parent=self)
            return
        destinations = self._get_all_destinations()
        dialog = PatternDestDialog(self, "Add Pattern Mapping", self.template_dir, destinations)
        pattern, dest = dialog.pattern, dialog.dest
        if not pattern or not dest:
            return
        if pattern in self.mappings:
            messagebox.showwarning("Duplicate Pattern", "This pattern already exists.")
            return
        self.mappings[pattern] = dest
        self._refresh_mapping_table()

    def _edit_rule(self):
        if not self.template_dir or not os.path.exists(self.template_dir):
            messagebox.showerror("No Template Directory", "Please select a mapping file first.", parent=self)
            return
        selected = self.mapping_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a mapping to edit.")
            return
        item = selected[0]
        pattern, dest = self.mapping_table.item(item, "values")
        destinations = self._get_all_destinations()
        dialog = PatternDestDialog(self, "Edit Pattern Mapping", self.template_dir, destinations, initial_pattern=pattern, initial_dest=dest)
        new_pattern, new_dest = dialog.pattern, dialog.dest
        if not new_pattern or not new_dest:
            return
        if new_pattern != pattern and new_pattern in self.mappings:
            messagebox.showwarning("Duplicate Pattern", "This pattern already exists.")
            return
        del self.mappings[pattern]
        self.mappings[new_pattern] = new_dest
        self._refresh_mapping_table()

    def _remove_rule(self):
        selected = self.mapping_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a mapping to remove.")
            return
        item = selected[0]
        pattern, _ = self.mapping_table.item(item, "values")
        del self.mappings[pattern]
        self._refresh_mapping_table()

    def _move_up(self):
        selected = self.mapping_table.selection()
        if not selected or self.mapping_table.index(selected[0]) == 0:
            return
        item = selected[0]
        index = self.mapping_table.index(item)
        keys = list(self.mappings.keys())
        key = keys[index]
        keys.insert(index - 1, keys.pop(index))
        new_mappings = {k: self.mappings[k] for k in keys}
        self.mappings = new_mappings
        self._refresh_mapping_table()
        self.mapping_table.selection_set(self.mapping_table.get_children()[index - 1])

    def _move_down(self):
        selected = self.mapping_table.selection()
        if not selected or self.mapping_table.index(selected[0]) == len(self.mappings) - 1:
            return
        item = selected[0]
        index = self.mapping_table.index(item)
        keys = list(self.mappings.keys())
        key = keys[index]
        keys.insert(index + 1, keys.pop(index))
        new_mappings = {k: self.mappings[k] for k in keys}
        self.mappings = new_mappings
        self._refresh_mapping_table()
        self.mapping_table.selection_set(self.mapping_table.get_children()[index + 1])

    def _save(self):
        if not self.mapping_path:
            messagebox.showerror("No Mapping File", "No mapping file selected to save.")
            return
        utils.MappingUtils.save_mapping(self.mapping_path, self.mappings)
        if self.on_save_callback:
            self.on_save_callback()
        self.destroy()

# For testing layout only
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    MappingEditor(root)
    root.mainloop()