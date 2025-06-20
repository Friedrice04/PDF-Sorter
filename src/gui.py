import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading

from tkinterdnd2 import DND_FILES, TkinterDnD

from . import sorter, utils
from .mapping_editor.editor import MappingEditor
from .utils import (
    load_settings, save_settings,
    LAST_MAPPING_KEY, MAPPINGS_DIR
)

class FileSorterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR File Sorter")
        self.root.geometry("550x480")

        # --- Modern Theme Setup ---
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # --- Drag & Drop Setup ---
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self._handle_drop)

        self.mapping_path = None
        self.settings = load_settings()
        self.deep_audit = ctk.BooleanVar()
        self.first_page_only = ctk.BooleanVar(value=True)
        self.root.minsize(450, 450)

        self._build_widgets()
        self._populate_mappings()

    def update_status(self, message):
        """Callback function to update the status label from the sorter."""
        self.root.after(0, self.status_label.configure, {"text": message})

    def _build_widgets(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # --- Mapping Selection ---
        mapping_frame = ctk.CTkFrame(self.root)
        mapping_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        mapping_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(mapping_frame, text="Mapping:").grid(row=0, column=0, padx=(10, 5))
        self.mapping_combo = ctk.CTkComboBox(mapping_frame, state="readonly")
        self.mapping_combo.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        edit_mapping_btn = ctk.CTkButton(mapping_frame, text="Edit", width=50, command=self._open_mapping_editor)
        edit_mapping_btn.grid(row=0, column=2, padx=(5, 10))

        # --- Folder List ---
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # The CTkTextbox will automatically use the theme colors.
        # The manual color lookup is no longer needed and has been removed.
        
        self.folder_listbox = ctk.CTkTextbox(main_frame, border_width=2)
        self.folder_listbox.grid(row=0, column=0, rowspan=2, padx=(10, 5), pady=10, sticky="nsew")
        self.folder_listbox.configure(state="disabled") # Make it read-only

        add_folder_btn = ctk.CTkButton(main_frame, text="Add Folder", command=self._add_folder)
        add_folder_btn.grid(row=0, column=1, padx=(5, 10), pady=(10, 5), sticky="ew")
        
        remove_folder_btn = ctk.CTkButton(main_frame, text="Remove Selected", command=self._remove_folder)
        remove_folder_btn.grid(row=1, column=1, padx=(5, 10), pady=(5, 10), sticky="ew")

        # --- Options ---
        options_frame = ctk.CTkFrame(self.root)
        options_frame.grid(row=2, column=0, padx=10, pady=5)

        deep_audit_check = ctk.CTkCheckBox(options_frame, text="Deep Audit (slower)", variable=self.deep_audit)
        deep_audit_check.grid(row=0, column=0, padx=10, pady=10)

        first_page_check = ctk.CTkCheckBox(options_frame, text="Scan first page only", variable=self.first_page_only)
        first_page_check.grid(row=0, column=1, padx=10, pady=10)

        # --- Bottom Widgets ---
        bottom_frame = ctk.CTkFrame(self.root)
        bottom_frame.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="ew")
        bottom_frame.grid_columnconfigure(1, weight=1)

        self.sort_btn = ctk.CTkButton(bottom_frame, text="Sort", command=self._start_sort_thread)
        self.sort_btn.grid(row=0, column=0, padx=10, pady=10)

        help_btn = ctk.CTkButton(bottom_frame, text="Help", command=self._show_help)
        help_btn.grid(row=0, column=2, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(bottom_frame, text="Ready", anchor="w")
        self.status_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(self.root)
        self.progress_bar.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.progress_bar.set(0)

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

    def _update_folder_list(self):
        self.folder_listbox.configure(state="normal")
        self.folder_listbox.delete("1.0", "end")
        if self.folders_to_sort:
            self.folder_listbox.insert("1.0", "\n".join(self.folders_to_sort))
        self.folder_listbox.configure(state="disabled")

    def _add_folder(self):
        folder_path = filedialog.askdirectory(mustexist=True, title="Select Folder to Sort")
        if folder_path and folder_path not in self.folders_to_sort:
            self.folders_to_sort.append(folder_path)
            self._update_folder_list()

    def _remove_folder(self):
        # Since CTkTextbox doesn't have selection, we'll remove the last added folder
        if self.folders_to_sort:
            removed = self.folders_to_sort.pop()
            self.update_status(f"Removed: {os.path.basename(removed)}")
            self._update_folder_list()

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
        # Note: The editor window will still use the old style.
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
    # To use TkinterDnD2 with customtkinter, the root must be a TkinterDnD.Tk() instance.
    # This combines the functionality of both libraries.
    root = TkinterDnD.Tk()
    app = FileSorterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()