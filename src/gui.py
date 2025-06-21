import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk # Imported for the context menu
import threading

from tkinterdnd2 import DND_FILES, TkinterDnD

from src import sorter, utils
from src.mapping_editor.editor_gui import MappingEditor
from src.utils import (
    load_settings, save_settings,
    LAST_MAPPING_KEY, MAPPINGS_DIR
)

class FileSorterGUI:
    def __init__(self, root):
        self.root = root
        # Remove the default OS title bar
        self.root.overrideredirect(True)
        self.root.geometry("550x480")

        # Set a unique color and make it transparent to create rounded window corners
        TRANSPARENT_COLOR = '#000001'
        self.root.config(bg=TRANSPARENT_COLOR)
        self.root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self._handle_drop)

        self.mapping_path = None
        self.settings = load_settings()
        self.deep_audit = ctk.BooleanVar()
        self.first_page_only = ctk.BooleanVar(value=True)
        self.folders_to_sort = []
        self.selected_folder_path = None
        self.folder_widgets = {}
        self.root.minsize(450, 450)

        # For dragging the frameless window
        self._offset_x = 0
        self._offset_y = 0

        # Build widgets first, so we have a CTk widget to get theme colors from.
        self._build_widgets()
        self._create_context_menu()
        self._populate_mappings()

    def update_status(self, message):
        self.root.after(0, self.status_label.configure, {"text": message})

    def _create_context_menu(self):
        """Creates the right-click context menu and styles it to match the theme."""
        # Get colors from a CTk widget (main_container) instead of the root window.
        bg_color = self.main_container._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        fg_color = self.main_container._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        hover_color = self.main_container._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["hover_color"])
        # The disabled text color is part of the CTkButton theme, not CTkLabel.
        disabled_color = self.main_container._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["text_color_disabled"])

        self.context_menu = tk.Menu(self.root, tearoff=0,
            bg=bg_color,
            fg=fg_color,
            activebackground=hover_color,
            activeforeground=fg_color,
            disabledforeground=disabled_color,
            relief="flat",
            borderwidth=0
        )
        self.context_menu.add_command(label="Add Folder", command=self._add_folder)
        self.context_menu.add_command(label="Remove Selected Folder", command=self._remove_folder)

    def _show_context_menu(self, event):
        """Shows the right-click menu and enables/disables items."""
        # Disable 'Remove' if no folder is selected
        if self.selected_folder_path:
            self.context_menu.entryconfigure("Remove Selected Folder", state="normal")
        else:
            self.context_menu.entryconfigure("Remove Selected Folder", state="disabled")
        
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def _build_widgets(self):
        # Main container with a border to create the window frame effect.
        # Padding is removed (padx=0, pady=0) to eliminate the white border.
        self.main_container = ctk.CTkFrame(self.root, corner_radius=10)
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)

        # --- Custom Title Bar ---
        title_bar = ctk.CTkFrame(self.main_container, corner_radius=0)
        title_bar.pack(fill="x")
        
        title_label = ctk.CTkLabel(title_bar, text="OCR File Sorter", font=ctk.CTkFont(weight="bold"))
        title_label.pack(side="left", padx=10, pady=5)

        close_button = ctk.CTkButton(title_bar, text="✕", width=28, height=28, command=self.root.destroy)
        close_button.pack(side="right", padx=5, pady=5)

        # Bind events for dragging the window
        title_bar.bind("<ButtonPress-1>", self._start_move)
        title_bar.bind("<ButtonRelease-1>", self._stop_move)
        title_bar.bind("<B1-Motion>", self._do_move)
        title_label.bind("<ButtonPress-1>", self._start_move)
        title_label.bind("<ButtonRelease-1>", self._stop_move)
        title_label.bind("<B1-Motion>", self._do_move)

        # --- Main Content Area ---
        content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # --- Mapping Selection ---
        mapping_frame = ctk.CTkFrame(content_frame)
        mapping_frame.grid(row=0, column=0, sticky="ew")
        mapping_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(mapping_frame, text="Mapping:").grid(row=0, column=0, padx=(10, 5), pady=10)
        self.mapping_combo = ctk.CTkComboBox(mapping_frame, state="readonly", border_width=0)
        self.mapping_combo.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        edit_mapping_btn = ctk.CTkButton(mapping_frame, text="Edit", width=50, command=self._open_mapping_editor)
        edit_mapping_btn.grid(row=0, column=2, padx=(5, 10), pady=10)

        # --- Folder List ---
        main_frame = ctk.CTkFrame(content_frame)
        main_frame.grid(row=1, column=0, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        self.folder_list_frame = ctk.CTkScrollableFrame(main_frame, border_width=2)
        self.folder_list_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.folder_list_frame.bind("<Button-3>", self._show_context_menu)

        # Create a frame to hold the Add/Remove buttons for better alignment
        side_button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        side_button_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="n")

        add_folder_btn = ctk.CTkButton(side_button_frame, text="Add Folder", command=self._add_folder)
        add_folder_btn.pack(pady=(0, 5), fill="x")
        
        remove_folder_btn = ctk.CTkButton(side_button_frame, text="Remove Selected", command=self._remove_folder)
        remove_folder_btn.pack(pady=5, fill="x")

        # --- Options ---
        options_frame = ctk.CTkFrame(content_frame)
        options_frame.grid(row=2, column=0, sticky="ew")
        options_frame.grid_columnconfigure((0, 1), weight=1)

        deep_audit_check = ctk.CTkCheckBox(options_frame, text="Deep Audit (slower)", variable=self.deep_audit)
        deep_audit_check.pack(side="left", padx=20, pady=10)

        first_page_check = ctk.CTkCheckBox(options_frame, text="Scan first page only", variable=self.first_page_only)
        first_page_check.pack(side="right", padx=20, pady=10)

        # --- Bottom Widgets ---
        bottom_frame = ctk.CTkFrame(content_frame)
        bottom_frame.grid(row=3, column=0, pady=(10, 0), sticky="ew")
        bottom_frame.grid_columnconfigure(1, weight=1)

        self.sort_btn = ctk.CTkButton(bottom_frame, text="Sort", command=self._start_sort_thread)
        self.sort_btn.grid(row=0, column=0, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(bottom_frame, text="Ready", anchor="w")
        self.status_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        help_btn = ctk.CTkButton(bottom_frame, text="Help", command=self._show_help)
        help_btn.grid(row=0, column=2, padx=10, pady=10)

        self.progress_bar = ctk.CTkProgressBar(content_frame)
        self.progress_bar.grid(row=4, column=0, pady=10, sticky="ew")
        self.progress_bar.set(0)

    # --- Window Dragging Methods ---
    def _start_move(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def _stop_move(self, event):
        self._offset_x = None
        self._offset_y = None

    def _do_move(self, event):
        if self._offset_x is not None and self._offset_y is not None:
            new_x = self.root.winfo_x() + (event.x - self._offset_x)
            new_y = self.root.winfo_y() + (event.y - self._offset_y)
            self.root.geometry(f"+{new_x}+{new_y}")

    def _populate_mappings(self):
        mappings = utils.MappingUtils.get_available_mappings()
        self.mapping_combo.configure(values=mappings)
        last_mapping = self.settings.get(LAST_MAPPING_KEY)
        if last_mapping and last_mapping in mappings:
            self.mapping_combo.set(last_mapping)
        elif mappings:
            self.mapping_combo.set(mappings[0])
        self._on_mapping_select()
        self.mapping_combo.configure(command=self._on_mapping_select)

    def _on_mapping_select(self, choice=None):
        selected_mapping = self.mapping_combo.get()
        if selected_mapping:
            self.mapping_path = os.path.join(MAPPINGS_DIR, selected_mapping)
            self.settings[LAST_MAPPING_KEY] = selected_mapping
            save_settings(self.settings)

    def _on_folder_select(self, folder_path):
        if self.selected_folder_path and self.selected_folder_path in self.folder_widgets:
            self.folder_widgets[self.selected_folder_path].configure(fg_color="transparent")
        self.selected_folder_path = folder_path
        self.folder_widgets[folder_path].configure(fg_color=("gray70", "gray30"))

    def _update_folder_list(self):
        for widget in self.folder_list_frame.winfo_children():
            widget.destroy()
        self.folder_widgets.clear()

        for folder_path in self.folders_to_sort:
            # Display the full path instead of just the basename
            display_name = folder_path
            folder_button = ctk.CTkButton(
                self.folder_list_frame,
                text=display_name,
                fg_color="transparent",
                anchor="w",
                command=lambda p=folder_path: self._on_folder_select(p)
            )
            # Bind right-click to the button as well
            folder_button.bind("<Button-3>", self._show_context_menu)
            folder_button.pack(fill="x", padx=5, pady=2)
            self.folder_widgets[folder_path] = folder_button

        if self.selected_folder_path and self.selected_folder_path in self.folder_widgets:
            self.folder_widgets[self.selected_folder_path].configure(fg_color=("gray70", "gray30"))
        else:
            self.selected_folder_path = None

    def _add_folder(self):
        folder_path = filedialog.askdirectory(mustexist=True, title="Select Folder to Sort")
        if folder_path and folder_path not in self.folders_to_sort:
            self.folders_to_sort.append(folder_path)
            self._update_folder_list()

    def _remove_folder(self):
        if self.selected_folder_path:
            self.folders_to_sort.remove(self.selected_folder_path)
            self.update_status(f"Removed: {os.path.basename(self.selected_folder_path)}")
            self.selected_folder_path = None
            self._update_folder_list()
        else:
            self.update_status("No folder selected to remove.")

    def _handle_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        for item in paths:
            if os.path.isdir(item) and item not in self.folders_to_sort:
                self.folders_to_sort.append(item)
        self._update_folder_list()

    def _show_help(self):
        messagebox.showinfo(
            "Help",
            "1. Select a mapping file from the dropdown.\n"
            "2. Use the 'Edit' button to define keywords and destination folders.\n"
            "3. Add folders to sort by clicking 'Add Folder' or by dragging them into the window.\n"
            "4. Choose your sorting options (e.g., 'Scan first page only').\n"
            "5. Click 'Sort' to begin."
        )

    def _open_mapping_editor(self):
        def on_save_callback():
            selected = self.mapping_combo.get()
            self._populate_mappings()
            self.mapping_combo.set(selected)
        MappingEditor(self.root, on_save_callback=on_save_callback, mapping_path=self.mapping_path)

    def _start_sort_thread(self):
        self.sort_btn.configure(state="disabled")
        self.status_label.configure(text="Starting sort...")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        thread = threading.Thread(target=self._sort_files, daemon=True)
        thread.start()

    def _sort_files(self):
        mapping_path = self.mapping_path
        if not mapping_path or not os.path.isfile(mapping_path):
            self.root.after(0, utils.show_error, "Please select a valid mapping file.")
            self.sort_btn.configure(state="normal")
            return
        if not self.folders_to_sort:
            self.root.after(0, utils.show_error, "Please add at least one folder to sort.")
            self.sort_btn.configure(state="normal")
            return

        try:
            sorter_obj = sorter.Sorter(
                mapping_path,
                status_callback=self.update_status
            )
            deep_audit = self.deep_audit.get()
            first_page_only = self.first_page_only.get()
            
            sorter_obj.sort_files(self.folders_to_sort, deep_audit=deep_audit, first_page_only=first_page_only)

            self.root.after(0, messagebox.showinfo, "Success", "Files sorted successfully!")
        except Exception as e:
            self.root.after(0, utils.show_error, f"An error occurred during sorting:\n{e}")
        finally:
            def final_update():
                self.sort_btn.configure(state="normal")
                self.status_label.configure(text="Ready")
                self.progress_bar.stop()
                self.progress_bar.configure(mode="determinate")
                self.progress_bar.set(0)
            self.root.after(0, final_update)

def main():
    root = TkinterDnD.Tk()
    app = FileSorterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()