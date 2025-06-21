import os
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from src import utils
from src.utils import ToolTip
from src.mapping_editor.dialogs import NewMappingDialog, PatternDestDialog
from src.mapping_editor.mapping_table import MappingTable
from src.mapping_editor.template_tree import TemplateTree
from src.mapping_editor.editor_logic import EditorLogic
from src.mapping_editor.editor_actions import EditorActions

MAPPINGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../mappings"))

class MappingEditor(ctk.CTkToplevel):
    """
    Main window for editing file sorting mappings, styled to match the main GUI.
    This class is the 'View' in a Model-View-Controller architecture.
    """
    def __init__(self, master, on_save_callback=None, mapping_path=None):
        super().__init__(master)
        self.on_save_callback = on_save_callback

        # --- Window Setup ---
        self.geometry("1000x650")
        self.overrideredirect(True) # Frameless

        # Make window rounded
        TRANSPARENT_COLOR = '#000001'
        self.config(bg=TRANSPARENT_COLOR)
        self.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)

        # For dragging the frameless window
        self._offset_x = 0
        self._offset_y = 0

        # --- MVC Setup ---
        self.logic = EditorLogic()
        self.actions = EditorActions(self, self.logic)

        # --- Build UI ---
        self._build_widgets()
        self._style_treeviews()
        self.protocol("WM_DELETE_WINDOW", self.actions.on_close_window)
        self.bind_all("<ButtonRelease-1>", self.actions.on_drag_release)

        # --- Initial Load ---
        if mapping_path:
            self.logic.load_mapping_file(mapping_path)
            self.refresh_all(reload_files=True)
        else:
            # Still need to load the list of files even if none is pre-selected
            self.update_mapping_file_list()

    def _build_widgets(self):
        # Main container with a border to create the window frame effect.
        self.main_container = ctk.CTkFrame(self, corner_radius=10)
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        # --- Custom Title Bar ---
        self._build_title_bar()

        # --- Main Content Area ---
        content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # --- Top frame for mapping file selection ---
        file_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        file_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        file_frame.grid_columnconfigure(0, weight=1)

        self.mapping_file_var = tk.StringVar()
        self.mapping_file_combo = ctk.CTkComboBox(file_frame, variable=self.mapping_file_var, state="readonly", command=self.actions.on_mapping_file_selected)
        self.mapping_file_combo.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ToolTip(self.mapping_file_combo, "Select a mapping JSON file to edit.")

        search_btn = ctk.CTkButton(file_frame, text="Search...", width=80, command=self.actions.on_search_mapping)
        search_btn.grid(row=0, column=1, padx=5)
        ToolTip(search_btn, "Search for a mapping JSON file by name.")

        new_btn = ctk.CTkButton(file_frame, text="New Mapping", width=100, command=self.actions.on_new_mapping)
        new_btn.grid(row=0, column=2, padx=5)
        ToolTip(new_btn, "Create a new mapping file.")

        # --- Main Paned Area (using a grid) ---
        paned_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        paned_frame.grid(row=1, column=0, sticky="nsew")
        paned_frame.grid_columnconfigure(0, weight=3) # Left panel is larger
        paned_frame.grid_columnconfigure(1, weight=2) # Right panel is smaller
        paned_frame.grid_rowconfigure(0, weight=1)

        self._build_left_panel(paned_frame)
        self._build_right_panel(paned_frame)

        # --- Bottom frame for Save/Cancel ---
        bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="e", pady=(10, 0))
        
        cancel_btn = ctk.CTkButton(bottom_frame, text="Close", command=self.actions.on_close_window)
        cancel_btn.pack(side="right")
        save_btn = ctk.CTkButton(bottom_frame, text="Save", command=self.actions.on_save)
        save_btn.pack(side="right", padx=(0, 10))

    def _build_title_bar(self):
        title_bar = ctk.CTkFrame(self.main_container, corner_radius=0, height=40)
        title_bar.grid(row=0, column=0, sticky="ew")
        
        self.title_label = ctk.CTkLabel(title_bar, text="Mapping Editor", font=ctk.CTkFont(weight="bold"))
        self.title_label.pack(side="left", padx=15, pady=10)
        
        close_button = ctk.CTkButton(title_bar, text="✕", width=30, height=30, command=self.actions.on_close_window)
        close_button.pack(side="right", padx=5, pady=5)

        title_bar.bind("<ButtonPress-1>", self._start_move)
        title_bar.bind("<ButtonRelease-1>", self._stop_move)
        title_bar.bind("<B1-Motion>", self._do_move)
        self.title_label.bind("<ButtonPress-1>", self._start_move)
        self.title_label.bind("<ButtonRelease-1>", self._stop_move)
        self.title_label.bind("<B1-Motion>", self._do_move)

    def _build_left_panel(self, parent):
        left_frame = ctk.CTkFrame(parent)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left_frame, text="Phrase / Keyword → Destination", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(5, 2))
        
        self.mapping_table = MappingTable(left_frame, on_item_drag=self.actions.on_item_drag_start)
        self.mapping_table.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.mapping_table.bind("<B1-Motion>", lambda e: self.actions.on_drag_motion())
        self.mapping_table.bind("<Double-Button-1>", lambda e: self.actions.on_edit_rule())
        self._build_mapping_table_menu()
        self.mapping_table.bind("<Button-3>", self._show_mapping_table_menu)
        ToolTip(self.mapping_table, "Phrases and their destination folders. Drag a phrase onto a folder to assign.")

        button_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(5, 10))
        button_frame.grid_columnconfigure((0,1,2,3), weight=1)
        ctk.CTkButton(button_frame, text="Add", command=self.actions.on_add_rule).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(button_frame, text="Remove", command=self.actions.on_remove_rule).grid(row=0, column=1, sticky="ew", padx=(0, 5))
        ctk.CTkButton(button_frame, text="Move Up", command=lambda: self.actions.on_move_rule("up")).grid(row=0, column=2, sticky="ew", padx=(0, 5))
        ctk.CTkButton(button_frame, text="Move Down", command=lambda: self.actions.on_move_rule("down")).grid(row=0, column=3, sticky="ew")

    def _build_right_panel(self, parent):
        right_frame = ctk.CTkFrame(parent)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right_frame, text="Template Directory Structure", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(5, 2))

        self.template_tree = TemplateTree(right_frame, self.logic.template_dir)
        self.template_tree.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self._build_template_tree_menu()
        self.template_tree.bind("<Button-3>", self._show_template_tree_menu)
        ToolTip(self.template_tree, "Visualize and manage the template directory structure.")

        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(5, 10))
        btn_frame.grid_columnconfigure((0,1,2,3), weight=1)
        ctk.CTkButton(btn_frame, text="New Folder", command=self.template_tree.add_folder).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(btn_frame, text="Delete Folder", command=self.template_tree.delete_folder).grid(row=0, column=1, sticky="ew", padx=(0, 5))
        ctk.CTkButton(btn_frame, text="Refresh", command=self.refresh_template_tree).grid(row=0, column=2, sticky="ew", padx=(0, 5))
        ctk.CTkButton(btn_frame, text="Auto-Build", command=self.actions.on_autobuild_tree).grid(row=0, column=3, sticky="ew")

    def _style_treeviews(self):
        """Applies CTk theme colors to the ttk.Treeview widgets."""
        bg_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        text_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        header_bg = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        select_bg = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["hover_color"])

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0)
        style.map("Treeview", background=[("selected", select_bg)])
        style.configure("Treeview.Heading", background=header_bg, foreground=text_color, relief="flat")
        style.map("Treeview.Heading", background=[("active", select_bg)])
        self.update_idletasks()

    def _build_menu(self):
        """Helper to create a themed tk.Menu."""
        bg = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        fg = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        hover = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["hover_color"])
        disabled = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["text_color_disabled"])
        
        return tk.Menu(self, tearoff=0, bg=bg, fg=fg, activebackground=hover,
                       activeforeground=fg, disabledforeground=disabled, relief="flat")

    def _build_mapping_table_menu(self):
        self.mapping_table_menu = self._build_menu()
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
        self.template_tree_menu = self._build_menu()
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

    # --- Window Dragging Methods ---
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

    # --- UI Update Methods (called by Actions) ---
    def refresh_all(self, reload_files=False):
        if reload_files:
            self.update_mapping_file_list()
        self.update_mapping_file_display(self.logic.mapping_path)
        self.refresh_mapping_table()
        self.refresh_template_tree()
        self.set_dirty(self.logic.is_dirty)

    def refresh_mapping_table(self):
        self.mapping_table.refresh(self.logic.mappings)

    def refresh_template_tree(self):
        self.template_tree.template_dir = self.logic.template_dir
        self.template_tree._populate_tree()

    def set_dirty(self, is_dirty):
        title = "Mapping Editor"
        if is_dirty:
            self.title_label.configure(text=f"{title} *")
        else:
            self.title_label.configure(text=title)
        self.logic.is_dirty = is_dirty

    def update_mapping_file_list(self):
        self.mapping_file_combo.configure(values=utils.MappingUtils.get_available_mappings())

    def update_mapping_file_display(self, mapping_path):
        self.mapping_file_var.set(os.path.basename(mapping_path) if mapping_path else "")

    def highlight_template_tree_under_pointer(self):
        self.clear_drag_highlight()
        y = self.template_tree.winfo_pointery() - self.template_tree.winfo_rooty()
        item = self.template_tree.identify_row(y)
        if item:
            highlight_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["hover_color"])
            self.template_tree.tag_configure("drag_highlight", background=highlight_color)
            self.template_tree.item(item, tags=("drag_highlight",))

    def clear_drag_highlight(self):
        # Find all items with the tag and remove it
        tagged_items = self.template_tree.tag_has("drag_highlight")
        for item in tagged_items:
            self.template_tree.item(item, tags=())

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