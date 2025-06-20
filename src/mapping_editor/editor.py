
import os
import tkinter as tk
from tkinter import ttk

from .template_tree import TemplateTree
from .mapping_table import MappingTable
from .editor_logic import EditorLogic
from .editor_actions import EditorActions
from src.utils import ToolTip

MAPPINGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../mappings"))

class MappingEditor(tk.Toplevel):
    """
    Main window for editing file sorting mappings.
    This class is responsible for building the UI (the View).
    """
    def __init__(self, master, on_save_callback=None, mapping_path=None):
        super().__init__(master)
        self.title("Mapping Editor")
        self.geometry("1000x600")
        self.on_save_callback = on_save_callback

        # Initialize the Model and Controller
        self.logic = EditorLogic()
        self.actions = EditorActions(self, self.logic)

        self._build_widgets()
        self.bind_all("<ButtonRelease-1>", self.actions.on_drag_release)
        self.protocol("WM_DELETE_WINDOW", self.actions.on_close_window)

        if mapping_path:
            self.logic.load_mapping_file(mapping_path)
            self.refresh_all()

    def _build_widgets(self):
        # --- Top Frame for Mapping File Selection ---
        file_frame = ttk.Frame(self)
        file_frame.pack(fill="x", padx=10, pady=(10, 0))
        self.mapping_file_var = tk.StringVar()
        self.mapping_file_combo = ttk.Combobox(file_frame, textvariable=self.mapping_file_var, state="readonly")
        self.mapping_file_combo.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.mapping_file_combo.bind("<<ComboboxSelected>>", self.actions.on_mapping_file_selected)
        ttk.Button(file_frame, text="New Mapping", command=self.actions.on_new_mapping).pack(side="left")

        # --- Main PanedWindow for Resizable Panes ---
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Left Pane: Mapping Table and Controls ---
        left_frame = self._build_left_pane(paned)
        paned.add(left_frame, weight=3)

        # --- Right Pane: Template Tree and Controls ---
        right_frame = self._build_right_pane(paned)
        paned.add(right_frame, weight=2)

        # --- Bottom Frame for Save/Cancel ---
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(bottom_frame, text="Save", command=self.actions.on_save).pack(side="right", padx=(5, 0))
        ttk.Button(bottom_frame, text="Cancel", command=self.actions.on_close_window).pack(side="right")

    def _build_left_pane(self, parent):
        left_frame = ttk.Frame(parent)
        ttk.Label(left_frame, text="Phrase / Keyword → Destination", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=5, pady=(0, 2))
        
        self.mapping_table = MappingTable(left_frame, on_item_drag=self.actions.on_item_drag_start)
        self.mapping_table.pack(fill="both", expand=True)
        self.mapping_table.bind("<Double-Button-1>", lambda e: self.actions.on_edit_rule())
        
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill="x", pady=(8, 0))
        ttk.Button(button_frame, text="Add", command=self.actions.on_add_rule).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(button_frame, text="Remove", command=self.actions.on_remove_rule).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(button_frame, text="Move Up", command=lambda: self.actions.on_move_rule("up")).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(button_frame, text="Move Down", command=lambda: self.actions.on_move_rule("down")).pack(side="left", fill="x", expand=True)
        
        return left_frame

    def _build_right_pane(self, parent):
        right_frame = ttk.Frame(parent)
        ttk.Label(right_frame, text="Template Directory Structure", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=5, pady=(0, 2))
        
        self.template_tree = TemplateTree(right_frame, self.logic.template_dir)
        self.template_tree.pack(fill="both", expand=True)
        
        self._build_template_tree_menu()
        self.template_tree.bind("<Button-3>", self._on_template_tree_right_click)

        template_btn_frame = ttk.Frame(right_frame)
        template_btn_frame.pack(fill="x", pady=(8, 0))
        ttk.Button(template_btn_frame, text="New Folder", command=self.template_tree.add_folder).pack(side="left", padx=(0, 5))
        ttk.Button(template_btn_frame, text="Delete Folder", command=self.template_tree.delete_folder).pack(side="left", padx=(0, 5))
        ttk.Button(template_btn_frame, text="Refresh", command=self.refresh_template_tree).pack(side="left")
        ttk.Button(template_btn_frame, text="Auto-Build Tree", command=self.actions.on_autobuild_tree).pack(side="left", padx=(5, 0))
        
        return right_frame

    def _build_template_tree_menu(self):
        self.template_tree_menu = tk.Menu(self, tearoff=0)
        self.template_tree_menu.add_command(label="Add Folder", command=self.template_tree.add_folder)
        self.template_tree_menu.add_command(label="Rename Folder", command=self.actions.on_rename_template_folder)
        self.template_tree_menu.add_command(label="Delete Folder", command=self.template_tree.delete_folder)

    def _on_template_tree_right_click(self, event):
        item = self.template_tree.identify_row(event.y)
        is_item_selected = bool(item)
        self.template_tree_menu.entryconfig("Rename Folder", state="normal" if is_item_selected else "disabled")
        self.template_tree_menu.entryconfig("Delete Folder", state="normal" if is_item_selected else "disabled")
        if is_item_selected:
            self.template_tree.selection_set(item)
        self.template_tree_menu.tk_popup(event.x_root, event.y_root)

    def set_dirty(self, dirty=True):
        """Mark the editor state as dirty (unsaved) and update title."""
        if dirty and not self.title().endswith(" *"):
            self.title(self.title() + " *")
        elif not dirty and self.title().endswith(" *"):
            self.title(self.title().rstrip(" *"))
        self.logic.is_dirty = dirty

    def refresh_mapping_table(self):
        """Refresh the mapping table with data from the logic module."""
        self.mapping_table.refresh(self.logic.mappings)

    def refresh_template_tree(self):
        """Refresh the template tree with data from the logic module."""
        self.template_tree.template_dir = self.logic.template_dir
        self.template_tree._populate_tree()

    def update_mapping_file_display(self, mapping_path):
        """Update the combobox and file list."""
        self.mapping_file_var.set(os.path.basename(mapping_path) if mapping_path else "")
        self.mapping_file_combo['values'] = [f for f in os.listdir(MAPPINGS_DIR) if f.endswith(".json")]

    def refresh_all(self, reload_files=False):
        """Refresh the entire UI."""
        if reload_files:
            self.update_mapping_file_display(self.logic.mapping_path)
        self.refresh_mapping_table()
        self.refresh_template_tree()
        self.set_dirty(self.logic.is_dirty)

# For testing layout only
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    editor = MappingEditor(root)
    editor.mainloop()
