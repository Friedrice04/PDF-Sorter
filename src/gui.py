import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
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
        self.root.title("OCR File Sorter")
        self.root.geometry("500x400")
        
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self._handle_drop)

        self.mapping_path = None
        self.settings = load_settings()
        self.deep_audit = tk.BooleanVar()
        self.first_page_only = tk.BooleanVar(value=True) # Default to True for speed
        self.root.minsize(300, 220)

        self._build_widgets()
        self._populate_mappings()

    def update_status(self, message):
        """Callback function to update the status label from the sorter."""
        self.root.after(0, self.status_label.config, {"text": message})

    def _build_widgets(self):
        # --- Menu Bar (Removed) ---
        # The help button is now at the bottom of the window.

        # --- Mapping Selection ---
        mapping_frame = ttk.Frame(self.root)
        mapping_frame.pack(pady=5, padx=10, fill=tk.X)
        
        ttk.Label(mapping_frame, text="Mapping:").pack(side="left")
        self.mapping_combo = ttk.Combobox(mapping_frame, state="readonly")
        self.mapping_combo.pack(side="left", fill=tk.X, expand=True, padx=(5, 5))
        
        edit_mapping_btn = ttk.Button(mapping_frame, text="Edit", command=self._open_mapping_editor)
        edit_mapping_btn.pack(side="left")

        # --- Folder List ---
        main_frame = ttk.Frame(self.root)
        main_frame.pack(pady=5, padx=10, fill="both", expand=True)
        
        listbox_frame = ttk.Frame(main_frame)
        listbox_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.folder_listbox = tk.Listbox(listbox_frame, selectmode=tk.EXTENDED, bg="#ffffff")
        self.folder_listbox.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.folder_listbox.dnd_bind('<<Drop>>', self._handle_drop)

        self.watermark_label = tk.Label(
            self.folder_listbox, text="Drag & Drop Folders Here", font=("Segoe UI", 16), fg="#cccccc", bg="#ffffff"
        )
        self._update_watermark()

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side="left", fill="y")
        
        add_folder_btn = ttk.Button(button_frame, text="Add Folder", command=self._add_folder)
        add_folder_btn.pack(fill="x", pady=(0, 5))
        
        remove_folder_btn = ttk.Button(button_frame, text="Remove Selected", command=self._remove_folder)
        remove_folder_btn.pack(fill="x")

        # --- Options ---
        options_frame = ttk.Frame(self.root)
        # This pack configuration centers the frame and its contents
        options_frame.pack(pady=5)

        deep_audit_check = ttk.Checkbutton(
            options_frame, text="Deep Audit (slower)", variable=self.deep_audit
        )
        deep_audit_check.pack(side="left", padx=5)
        utils.ToolTip(deep_audit_check, "Search for files in all subdirectories.")

        first_page_check = ttk.Checkbutton(
            options_frame, text="Scan first page only (faster)", variable=self.first_page_only
        )
        first_page_check.pack(side="left", padx=5)
        utils.ToolTip(first_page_check, "Speeds up sorting by only reading the first page of each PDF.")

        # --- Bottom Widgets ---
        # Widgets are packed from the bottom up. The first one packed is at the very bottom.
        
        # Progress Bar (at the very bottom)
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", mode="determinate")
        self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        # Status Label (above the progress bar)
        self.status_label = ttk.Label(self.root, text="Ready", anchor="w")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        # Bottom Buttons (above the status label)
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 5))

        self.sort_btn = ttk.Button(bottom_frame, text="Sort", command=self._start_sort_thread)
        self.sort_btn.pack(side=tk.LEFT)

        help_btn = ttk.Button(bottom_frame, text="Help", command=self._show_help)
        help_btn.pack(side=tk.RIGHT)

    def _populate_mappings(self):
        mappings = utils.MappingUtils.get_available_mappings()
        self.mapping_combo['values'] = mappings
        last_mapping = self.settings.get(LAST_MAPPING_KEY)
        if last_mapping and last_mapping in mappings:
            self.mapping_combo.set(last_mapping)
        elif mappings:
            self.mapping_combo.set(mappings[0])
        self._on_mapping_select(None)
        self.mapping_combo.bind("<<ComboboxSelected>>", self._on_mapping_select)

    def _on_mapping_select(self, event):
        selected_mapping = self.mapping_combo.get()
        if selected_mapping:
            self.mapping_path = os.path.join(MAPPINGS_DIR, selected_mapping)
            self.settings[LAST_MAPPING_KEY] = selected_mapping
            save_settings(self.settings)

    def _add_folder(self):
        folder_path = filedialog.askdirectory(mustexist=True, title="Select Folder to Sort")
        if folder_path:
            self.folder_listbox.insert(tk.END, folder_path)
            self._update_watermark()

    def _remove_folder(self):
        selected_indices = list(self.folder_listbox.curselection())
        for i in selected_indices[::-1]:
            self.folder_listbox.delete(i)
        self._update_watermark()

    def _handle_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        for item in paths:
            if os.path.isdir(item):
                self.folder_listbox.insert(tk.END, item)
        self._update_watermark()

    def _update_watermark(self):
        if self.folder_listbox.size() > 0:
            self.watermark_label.place_forget()
        else:
            self.watermark_label.place(relx=0.5, rely=0.5, anchor="center")

    def _show_help(self):
        messagebox.showinfo(
            "Help",
            "1. Select a mapping file from the dropdown.\n"
            "2. Use the 'Edit' button to define keywords and destination folders.\n"
            "3. Add folders to sort by clicking 'Add Folder' or by dragging them into the window.\n"
            "4. Choose your sorting options (e.g., 'Scan first page only').\n"
            "5. Click 'Start Sorting' to begin."
        )

    def _open_mapping_editor(self):
        def on_save_callback():
            selected = self.mapping_combo.get()
            self._populate_mappings()
            self.mapping_combo.set(selected)
        MappingEditor(self.root, on_save_callback=on_save_callback, mapping_path=self.mapping_path)

    def _start_sort_thread(self):
        self.sort_btn.config(state="disabled")
        self.status_label.config(text="Starting sort...")
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start()
        thread = threading.Thread(target=self._sort_files, daemon=True)
        thread.start()

    def _sort_files(self):
        mapping_path = self.mapping_path
        folders = self.folder_listbox.get(0, tk.END)
        if not mapping_path or not os.path.isfile(mapping_path):
            self.root.after(0, utils.show_error, "Please select a valid mapping file.")
            self.sort_btn.config(state="normal")
            return
        if not folders:
            self.root.after(0, utils.show_error, "Please add at least one folder to sort.")
            self.sort_btn.config(state="normal")
            return

        try:
            sorter_obj = sorter.Sorter(
                mapping_path,
                status_callback=self.update_status
            )
            deep_audit = self.deep_audit.get()
            first_page_only = self.first_page_only.get()
            
            sorter_obj.sort_files(folders, deep_audit=deep_audit, first_page_only=first_page_only)

            self.root.after(0, messagebox.showinfo, "Success", "Files sorted successfully!")
        except Exception as e:
            self.root.after(0, utils.show_error, f"An error occurred during sorting:\n{e}")
        finally:
            def final_update():
                self.sort_btn.config(state="normal")
                self.status_label.config(text="Ready")
                self.progress_bar.stop()
                self.progress_bar.config(mode="determinate")
                self.progress_bar['value'] = 0
            self.root.after(0, final_update)

def main():
    root = TkinterDnD.Tk()
    app = FileSorterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()