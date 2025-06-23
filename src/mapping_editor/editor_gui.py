import os
import tkinter as tk
from tkinter import ttk, messagebox

from src import utils
from src.utils import ToolTip
from src.mapping_editor.dialogs import NewMappingDialog, PatternDestDialog
from src.mapping_editor.mapping_table import MappingTable
from src.mapping_editor.template_tree import TemplateTree
from src.mapping_editor.editor_logic import EditorLogic
from src.mapping_editor.editor_actions import EditorActions

MAPPINGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../mappings"))

class MappingEditor(tk.Toplevel):
    """
    Main window for editing file sorting mappings using standard tkinter widgets.
    This class is the 'View' in a Model-View-Controller architecture.
    """
    def __init__(self, master, on_save_callback=None, mapping_path=None):
        super().__init__(master)
        self.title("Mapping Editor")
        self.geometry("1000x650")
        self.on_save_callback = on_save_callback

        # Instantiate Logic (Model) and Actions (Controller)
        self.logic = EditorLogic()
        self.actions = EditorActions(self, self.logic)

        self._build_widgets()
        self.protocol("WM_DELETE_WINDOW", self.actions.on_close_window)
        self.bind_all("<ButtonRelease-1>", self.actions.on_drag_release)

        # Initial load if a mapping path is provided
        if mapping_path:
            self.logic.load_mapping_file(mapping_path)
        self.refresh_all(reload_files=True)

    def _build_widgets(self):
        # --- Main container ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1) # The paned window will expand

        # --- Top frame for mapping file selection ---
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        file_frame.grid_columnconfigure(0, weight=1)

        self.mapping_file_var = tk.StringVar()
        self.mapping_file_combo = ttk.Combobox(file_frame, textvariable=self.mapping_file_var, state="readonly")
        self.mapping_file_combo.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.mapping_file_combo.bind("<<ComboboxSelected>>", self.actions.on_mapping_file_selected)
        ToolTip(self.mapping_file_combo, "Select a mapping JSON file to edit.")

        search_btn = ttk.Button(file_frame, text="Search...", command=self.actions.on_search_mapping)
        search_btn.grid(row=0, column=1, padx=(0, 5))
        ToolTip(search_btn, "Search for a mapping JSON file by name.")

        new_btn = ttk.Button(file_frame, text="New Mapping", command=self.actions.on_new_mapping)
        new_btn.grid(row=0, column=2, padx=(0, 5))
        ToolTip(new_btn, "Create a new mapping file.")

        help_btn = ttk.Button(file_frame, text="Help", command=self._show_help)
        help_btn.grid(row=0, column=3)
        ToolTip(help_btn, "Show information about how to use the editor.")

        # --- Naming Scheme Frame ---
        scheme_frame = ttk.Frame(main_frame)
        scheme_frame.grid(row=1, column=0, sticky="ew", pady=5)
        scheme_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(scheme_frame, text="File Naming Scheme:").grid(row=0, column=0, padx=(0, 5))
        self.naming_scheme_var = tk.StringVar()
        self.naming_scheme_entry = ttk.Entry(scheme_frame, textvariable=self.naming_scheme_var)
        self.naming_scheme_entry.grid(row=0, column=1, sticky="ew")
        self.naming_scheme_var.trace_add("write", lambda *args: self.logic.set_naming_scheme(self.naming_scheme_var.get()))
        ToolTip(self.naming_scheme_entry, "Define the new filename.\nPlaceholders: {rule_name}, {phrase}, {original_filename}, {date}, {time}, {ext}")

        # --- Main PanedWindow for resizable split view ---
        paned = ttk.PanedWindow(main_frame, orient="horizontal")
        paned.grid(row=2, column=0, sticky="nsew", pady=5)

        self._build_left_panel(paned)
        self._build_right_panel(paned)

        # --- Bottom frame for Save/Cancel ---
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=3, column=0, sticky="e", pady=(10, 0))
        
        save_btn = ttk.Button(bottom_frame, text="Save", command=self.actions.on_save)
        save_btn.pack(side="right", padx=(5, 0))
        close_btn = ttk.Button(bottom_frame, text="Close", command=self.actions.on_close_window)
        close_btn.pack(side="right")

    def _build_left_panel(self, parent):
        left_frame = ttk.Frame(parent, padding=5)
        parent.add(left_frame, weight=3)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)

        ttk.Label(left_frame, text="Mapping Rules", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.mapping_table = MappingTable(left_frame, on_item_drag=self.actions.on_item_drag_start)
        self.mapping_table.grid(row=1, column=0, sticky="nsew")
        self.mapping_table.bind("<B1-Motion>", lambda e: self.actions.on_drag_motion())
        self.mapping_table.bind("<Double-Button-1>", lambda e: self.actions.on_edit_rule())
        self._build_mapping_table_menu()
        self.mapping_table.bind("<Button-3>", self._show_mapping_table_menu)
        ToolTip(self.mapping_table, "Phrases and their destination folders. Drag a phrase onto a folder to assign.")

        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        button_frame.grid_columnconfigure((0,1,2,3), weight=1)
        ttk.Button(button_frame, text="Add", command=self.actions.on_add_rule).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(button_frame, text="Remove", command=self.actions.on_remove_rule).grid(row=0, column=1, sticky="ew", padx=(0, 5))
        ttk.Button(button_frame, text="Move Up", command=lambda: self.actions.on_move_rule("up")).grid(row=0, column=2, sticky="ew", padx=(0, 5))
        ttk.Button(button_frame, text="Move Down", command=lambda: self.actions.on_move_rule("down")).grid(row=0, column=3, sticky="ew")

    def _build_right_panel(self, parent):
        right_frame = ttk.Frame(parent, padding=5)
        parent.add(right_frame, weight=2)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)

        ttk.Label(right_frame, text="Template Directory", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.template_tree = TemplateTree(right_frame, self.logic.template_dir)
        self.template_tree.grid(row=1, column=0, sticky="nsew")
        self._build_template_tree_menu()
        self.template_tree.bind("<Button-3>", self._show_template_tree_menu)
        ToolTip(self.template_tree, "Visualize and manage the template directory structure.")

        btn_frame = ttk.Frame(right_frame)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(btn_frame, text="New Folder", command=self.template_tree.add_folder).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="Delete Folder", command=self.template_tree.delete_folder).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_template_tree).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="Auto-Build", command=self.actions.on_autobuild_tree).pack(side="left")

    def _build_mapping_table_menu(self):
        self.mapping_table_menu = tk.Menu(self, tearoff=0)
        self.mapping_table_menu.add_command(label="Add Rule", command=self.actions.on_add_rule)
        self.mapping_table_menu.add_command(label="Edit Rule", command=self.actions.on_edit_rule)
        self.mapping_table_menu.add_command(label="Remove Rule", command=self.actions.on_remove_rule)

    def _show_mapping_table_menu(self, event):
        is_item_selected = bool(self.mapping_table.identify_row(event.y))
        if is_item_selected:
            self.mapping_table.selection_set(self.mapping_table.identify_row(event.y))
        
        self.mapping_table_menu.entryconfig("Edit Rule", state="normal" if is_item_selected else "disabled")
        self.mapping_table_menu.entryconfig("Remove Rule", state="normal" if is_item_selected else "disabled")
        self.mapping_table_menu.tk_popup(event.x_root, event.y_root)

    def _build_template_tree_menu(self):
        self.template_tree_menu = tk.Menu(self, tearoff=0)
        self.template_tree_menu.add_command(label="Add Folder", command=self.template_tree.add_folder)
        self.template_tree_menu.add_command(label="Rename Folder", command=self.actions.on_rename_template_folder)
        self.template_tree_menu.add_command(label="Delete Folder", command=self.template_tree.delete_folder)

    def _show_template_tree_menu(self, event):
        is_item_selected = bool(self.template_tree.identify_row(event.y))
        if is_item_selected:
            self.template_tree.selection_set(self.template_tree.identify_row(event.y))

        self.template_tree_menu.entryconfig("Rename Folder", state="normal" if is_item_selected else "disabled")
        self.template_tree_menu.entryconfig("Delete Folder", state="normal" if is_item_selected else "disabled")
        self.template_tree_menu.tk_popup(event.x_root, event.y_root)

    def _show_help(self):
        """Displays a help message box explaining the editor's features."""
        help_title = "Mapping Editor Help"
        help_message = """
How to Use the Mapping Editor

1. Mapping Rules
   - The main table on the left shows your mapping rules.
   - Rule Name: A friendly, descriptive name for the rule.
   - Phrase/Keyword: A unique piece of text to search for inside a PDF. This is the key for the rule.
   - Destination Folder: The folder where the matched file will be moved, relative to the template directory.

2. Template Directory
   - The tree on the right shows the folder structure where your files will be sorted.
   - You can create, rename, and delete folders here.
   - Drag & Drop: Drag a rule from the left table and drop it onto a folder on the right to quickly set its destination.

3. File Naming Scheme
   - Define how your sorted files will be named using placeholders.
   - Available Placeholders:
     {rule_name}, {phrase}, {original_filename}, {date}, {time}, {ext}

4. Saving
   - An asterisk (*) in the window title means you have unsaved changes.
   - Click 'Save' to write your changes to the JSON mapping file.
"""
        messagebox.showinfo(help_title, help_message, parent=self)

    # --- UI Update Methods (called by Actions) ---

    def refresh_all(self, reload_files=False):
        if reload_files:
            self.update_mapping_file_list()
        self.update_mapping_file_display(self.logic.mapping_path)
        self.naming_scheme_var.set(self.logic.naming_scheme) # Update naming scheme field
        self.refresh_mapping_table()
        self.refresh_template_tree()
        self.set_dirty(self.logic.is_dirty)

    def refresh_mapping_table(self):
        self.mapping_table.refresh(self.logic.mappings)

    def refresh_template_tree(self):
        self.template_tree.template_dir = self.logic.template_dir
        self.template_tree._populate_tree()

    def set_dirty(self, is_dirty):
        """Update window title to show unsaved changes state."""
        title = "Mapping Editor"
        if is_dirty:
            self.title(f"{title} *")
        else:
            self.title(title)
        self.logic.is_dirty = is_dirty

    def update_mapping_file_list(self):
        self.mapping_file_combo["values"] = utils.MappingUtils.get_available_mappings()

    def update_mapping_file_display(self, mapping_path):
        self.mapping_file_var.set(os.path.basename(mapping_path) if mapping_path else "")

    def highlight_template_tree_under_pointer(self):
        self.clear_drag_highlight()
        y = self.template_tree.winfo_pointery() - self.template_tree.winfo_rooty()
        item = self.template_tree.identify_row(y)
        if item:
            self.template_tree.tag_configure("drag_highlight", background="#a1e3f7")
            self.template_tree.item(item, tags=("drag_highlight",))

    def clear_drag_highlight(self):
        def _clear_recursive(item):
            self.template_tree.item(item, tags=())
            for child in self.template_tree.get_children(item):
                _clear_recursive(child)
        for item in self.template_tree.get_children(""):
            _clear_recursive(item)

    # --- Drag and drop logic for assigning destination folders ---

    def _on_item_drag_event(self, action, item, event=None):
        if action == "start":
            self._dragged_item = item
            self._dragging = True
        elif action == "motion":
            if self._dragging:
                self.highlight_template_tree_under_pointer()

    def _on_drag_motion_context(self, event):
        if self._dragging and self._dragged_item:
            widget = event.widget
            if widget == self.template_tree:
                self._drag_context = "template"
                self.highlight_template_tree_under_pointer()
            else:
                self._drag_context = None

    def _on_drag_release(self, event):
        if not self._dragging or not self._dragged_item:
            return
        widget = self.winfo_containing(self.winfo_pointerx(), self.winfo_pointery())
        if widget == self.template_tree:
            x = self.template_tree.winfo_pointerx() - self.template_tree.winfo_rootx()
            y = self.template_tree.winfo_pointery() - self.template_tree.winfo_rooty()
            dest_item = self.template_tree.identify_row(y)
            if dest_item:
                rel_path = self.template_tree.item(dest_item, "values")[0]
                self._highlight_drop_target(dest_item)
            else:
                rel_path = "."
            if self._dragged_item in self.logic.mappings:
                if self.logic.mappings[self._dragged_item] != rel_path:
                    self.logic.mappings[self._dragged_item] = rel_path
                    self.refresh_mapping_table()
                    self.set_dirty(True)
        self._dragged_item = None
        self._dragging = False
        self._drag_context = None

    def _highlight_drop_target(self, item):
        self.template_tree.tag_configure("drop_highlight", background="#7fe3a1")
        self.template_tree.item(item, tags=("drop_highlight",))
        self.after(350, lambda: self.template_tree.item(item, tags=()))

    # --- End drag and drop logic ---

    def _add_rule(self):
        if not self.logic.template_dir or not os.path.exists(self.logic.template_dir):
            utils.show_error("No Template Directory", "Please select a mapping file first.", parent=self)
            return
        destinations = self.logic.get_all_destinations()
        dialog = PatternDestDialog(self, "Add Phrase/Keyword Mapping", self.logic.template_dir, destinations)
        phrase, dest = dialog.phrase, dialog.dest
        if not phrase or not dest:
            return
        if phrase in self.logic.mappings:
            utils.show_warning("Duplicate Phrase/Keyword", "This phrase or keyword already exists.")
            return
        self.logic.mappings[phrase] = dest
        self.refresh_mapping_table()
        self.set_dirty(True)

    def _edit_rule(self):
        if not self.logic.template_dir or not os.path.exists(self.logic.template_dir):
            utils.show_error("No Template Directory", "Please select a mapping file first.", parent=self)
            return
        selected = self.mapping_table.selection()
        if not selected:
            utils.show_warning("No Selection", "Please select a mapping to edit.")
            return
        item = selected[0]
        phrase, dest = self.mapping_table.item(item, "values")
        destinations = self.logic.get_all_destinations()
        dialog = PatternDestDialog(self, "Edit Phrase/Keyword Mapping", self.logic.template_dir, destinations, initial_phrase=phrase, initial_dest=dest)
        new_phrase, new_dest = dialog.phrase, dialog.dest
        if not new_phrase or not new_dest:
            return
        if new_phrase != phrase and new_phrase in self.logic.mappings:
            utils.show_warning("Duplicate Phrase/Keyword", "This phrase or keyword already exists.")
            return
        del self.logic.mappings[phrase]
        self.logic.mappings[new_phrase] = new_dest
        self.refresh_mapping_table()
        self.set_dirty(True)

    def _remove_rule(self):
        selected = self.mapping_table.selection()
        if not selected:
            utils.show_warning("No Selection", "Please select a mapping to remove.")
            return
        item = selected[0]
        phrase, _ = self.mapping_table.item(item, "values")
        del self.logic.mappings[phrase]
        self.refresh_mapping_table()
        self.set_dirty(True)

    def _move_up(self):
        selected = self.mapping_table.selection()
        if not selected or self.mapping_table.index(selected[0]) == 0:
            return
        item = selected[0]
        index = self.mapping_table.index(item)
        keys = list(self.logic.mappings.keys())
        keys.insert(index - 1, keys.pop(index))
        new_mappings = {k: self.logic.mappings[k] for k in keys}
        self.logic.mappings = new_mappings
        self.refresh_mapping_table()
        self.mapping_table.selection_set(self.mapping_table.get_children()[index - 1])
        self.set_dirty(True)

    def _move_down(self):
        selected = self.mapping_table.selection()
        if not selected or self.mapping_table.index(selected[0]) == len(self.logic.mappings) - 1:
            return
        item = selected[0]
        index = self.mapping_table.index(item)
        keys = list(self.logic.mappings.keys())
        keys.insert(index + 1, keys.pop(index))
        new_mappings = {k: self.logic.mappings[k] for k in keys}
        self.logic.mappings = new_mappings
        self.refresh_mapping_table()
        self.mapping_table.selection_set(self.mapping_table.get_children()[index + 1])
        self.set_dirty(True)

    def _save(self):
        if not self.logic.mapping_path:
            utils.show_error("No Mapping File", "No mapping file selected to save.")
            return
        utils.MappingUtils.save_mapping(self.logic.mapping_path, self.logic.mappings)
        self.set_dirty(False)
        if self.on_save_callback:
            self.on_save_callback()
        utils.show_info("Saved", "Mapping saved successfully.", parent=self)

# For testing layout only
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    MappingEditor(root)
    root.mainloop()