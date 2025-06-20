import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

from tkinterdnd2 import DND_FILES, TkinterDnD

from . import sorter, utils
from .mapping_editor.editor import MappingEditor
from .utils import (
    load_settings, save_settings, resource_path,
    LAST_MAPPING_KEY, MAPPINGS_DIR
)

class FileSorterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR File Sorter")
        self.root.geometry("500x400")
        
        # Correctly register the window as a drop target for files
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self._handle_drop)

        self.mapping_path = None
        self.settings = load_settings()
        self.deep_audit = tk.BooleanVar()  # Initialize variable for the checkbox
        self.root.minsize(300, 220)

        self._build_widgets()
        self._populate_mappings()

    def update_status(self, message):
        """Callback function to update the status label from the sorter."""
        self.root.after(0, self.status_label.config, {"text": message})

    def _build_widgets(self):
        mapping_frame = ttk.LabelFrame(self.root, text="Mapping File")
        mapping_frame.pack(fill="x", padx=10, pady=5)

        self.mapping_combo = ttk.Combobox(mapping_frame, state="readonly")
        self.mapping_combo.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.mapping_combo.bind("<<ComboboxSelected>>", self._on_mapping_select)
        last_mapping = self.settings.get(LAST_MAPPING_KEY)
        if last_mapping and last_mapping in self.mapping_combo['values']:
            self.mapping_combo.set(last_mapping)
            self._on_mapping_select(None)

        edit_btn = ttk.Button(mapping_frame, text="Edit/Create Mapping", command=self._open_mapping_editor)
        edit_btn.pack(side="left", padx=5)
        utils.ToolTip(edit_btn, "Open the mapping editor to create or modify mapping files.")

        folder_frame = ttk.LabelFrame(self.root, text="Folders to Sort (Drag folders here or use Add Folder...)")
        folder_frame.pack(fill="both", expand=True, padx=10, pady=5)

        listbox_frame = ttk.Frame(folder_frame)
        listbox_frame.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)

        self.folder_listbox = tk.Listbox(listbox_frame, selectmode=tk.EXTENDED, bg="#ffffff")
        self.folder_listbox.place(relx=0, rely=0, relwidth=1, relheight=1)
        # Correctly bind the drop event to the existing handler
        self.folder_listbox.dnd_bind('<<Drop>>', self._handle_drop)

        self.watermark_label = tk.Label(
            self.folder_listbox, text="OCR FileSorter", font=("Arial", 16, "bold"), fg="#cccccc", bg="#ffffff"
        )
        self._update_watermark()

        listbox_frame.rowconfigure(0, weight=1)
        listbox_frame.columnconfigure(0, weight=1)
        self.folder_listbox.lift()

        button_frame = ttk.Frame(folder_frame)
        button_frame.pack(side="left", fill="y", padx=5, pady=5)

        add_folder_btn = ttk.Button(button_frame, text="Add Folder...", command=self._add_folder)
        add_folder_btn.pack(fill="x", pady=(0, 5))
        utils.ToolTip(add_folder_btn, "Add a folder to the list to be sorted.")

        # Correct the command to call the existing _remove_folder method
        remove_folder_btn = ttk.Button(button_frame, text="Remove Selected", command=self._remove_folder)
        remove_folder_btn.pack(fill="x")
        utils.ToolTip(remove_folder_btn, "Remove selected folders from the list.")

        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)
        folder_frame.rowconfigure(0, weight=1)
        folder_frame.columnconfigure(0, weight=1)

        deep_chk = ttk.Checkbutton(self.root, text="Deep Audit", variable=self.deep_audit)
        deep_chk.pack(padx=10, anchor="w")
        utils.ToolTip(deep_chk, "If checked, recursively move misplaced files to their correct folders after sorting.")

        self.sort_btn = ttk.Button(self.root, text="Start Sorting", command=self._start_sort_thread)
        self.sort_btn.pack(pady=10, padx=10, fill=tk.X)

        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", mode="determinate")
        self.progress_bar.pack(pady=5, padx=10, fill=tk.X)

        self.status_label = ttk.Label(self.root, text="Ready", anchor="w")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        self.folder_listbox.bind("<Configure>", lambda e: self._update_watermark())

    def _update_watermark(self):
        if self.folder_listbox.size() == 0:
            self.watermark_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.watermark_label.place_forget()

    def _populate_mappings(self):
        if not os.path.exists(MAPPINGS_DIR):
            os.makedirs(MAPPINGS_DIR)
        mapping_files = [f for f in os.listdir(MAPPINGS_DIR) if f.endswith(".json")]
        self.mapping_combo['values'] = mapping_files

        last_mapping = self.settings.get(LAST_MAPPING_KEY)
        if mapping_files:
            if last_mapping and last_mapping in mapping_files:
                self.mapping_combo.set(last_mapping)
                self.mapping_path = os.path.join(MAPPINGS_DIR, last_mapping)
            else:
                self.mapping_combo.current(0)
                self.mapping_path = os.path.join(MAPPINGS_DIR, mapping_files[0])
        else:
            self.mapping_path = None

    def _on_mapping_select(self, event):
        selected = self.mapping_combo.get()
        if selected:
            self.mapping_path = os.path.join(MAPPINGS_DIR, selected)
            self.settings[LAST_MAPPING_KEY] = selected
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
        # In this version, we assume dropped items are folders to be sorted
        for item in paths:
            if os.path.isdir(item):
                self.folder_listbox.insert(tk.END, item)
        self._update_watermark()

    def _show_help(self):
        """Shows a help dialog."""
        messagebox.showinfo(
            "Help",
            "1. Select a mapping file from the dropdown.\n"
            "2. Use the 'Edit Mapping' button to define keywords and destination folders.\n"
            "3. Add folders you want to sort by clicking 'Add Folder' or by dragging them into the window.\n"
            "4. Click 'Start Sorting' to begin."
        )

    def _open_mapping_editor(self):
        def on_save_callback():
            selected = self.mapping_combo.get()
            self.settings[LAST_MAPPING_KEY] = selected
            save_settings(self.settings)
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
            # The Sorter class is in the sorter module
            sorter_obj = sorter.Sorter(
                mapping_path,
                status_callback=self.update_status
            )
            deep_audit = self.deep_audit.get()
            
            # The sort_files method handles all folders. No loop needed here.
            sorter_obj.sort_files(folders, deep_audit=deep_audit)

            self.root.after(0, messagebox.showinfo, "Success", "Files sorted successfully!")
        except Exception as e:
            self.root.after(0, utils.show_error, f"An error occurred during sorting:\n{e}")
        finally:
            # Ensure GUI elements are re-enabled in the main thread
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