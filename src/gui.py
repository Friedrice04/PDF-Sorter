import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from sorter import FileSorter
from mapping_editor import MappingEditor
from utils import (
    MappingUtils,
    show_error,
    ToolTip
)

class FileSorterGUI:
    """
    Main GUI class for the File Sorter application.
    Handles user interaction, mapping selection, and sorting operations.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("File Sorter")
        self.mapping_path = None
        self.directory = None
        self.sort_mode = tk.StringVar(value="single")
        self.deep_audit = tk.BooleanVar(value=False)

        self._build_widgets()
        self._populate_mappings()

    def _show_help(self):
        """
        Show a help dialog explaining the design and usage.
        """
        message = (
            "File Sorter Help\n\n"
            "This tool sorts files into folders based on patterns defined in a mapping file.\n\n"
            "Sorting Modes:\n"
            "- Single Folder: Sorts files in the selected folder only.\n"
            "- Child Folders: Sorts files in each first-level subfolder.\n\n"
            "Deep Audit:\n"
            "When enabled, after sorting, the tool will recursively scan for misplaced files and move them to the correct folders.\n\n"
            "Use the Mapping Editor to create or modify mapping files.\n"
        )
        messagebox.showinfo("Help - File Sorter", message)

    def _build_widgets(self):
        """
        Build and layout all widgets in the main window.
        """

        # Mapping selection
        mapping_frame = ttk.LabelFrame(self.root, text="Mapping File")
        mapping_frame.pack(fill="x", padx=10, pady=5)

        self.mapping_combo = ttk.Combobox(mapping_frame, state="readonly")
        self.mapping_combo.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.mapping_combo.bind("<<ComboboxSelected>>", self._on_mapping_selected)
        ToolTip(self.mapping_combo, "Select a mapping file to use for sorting.")

        edit_btn = ttk.Button(mapping_frame, text="Edit/Create Mapping", command=self._open_mapping_editor)
        edit_btn.pack(side="left", padx=5)
        ToolTip(edit_btn, "Open the mapping editor to create or modify mapping files.")

        # Directory selection
        dir_frame = ttk.LabelFrame(self.root, text="Directory to Sort")
        dir_frame.pack(fill="x", padx=10, pady=5)

        self.dir_entry = ttk.Entry(dir_frame)
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ToolTip(self.dir_entry, "Path to the folder you want to sort.")

        browse_btn = ttk.Button(dir_frame, text="Browse...", command=self._browse_directory)
        browse_btn.pack(side="left", padx=5)
        ToolTip(browse_btn, "Browse for the folder you want to sort.")

        # Sorting mode
        mode_frame = ttk.LabelFrame(self.root, text="Sorting Mode")
        mode_frame.pack(fill="x", padx=10, pady=5)

        single_radio = ttk.Radiobutton(mode_frame, text="Single Folder", variable=self.sort_mode, value="single")
        single_radio.pack(side="left", padx=5)
        ToolTip(single_radio, "Sort files in the selected folder only.")

        child_radio = ttk.Radiobutton(mode_frame, text="Child Folders", variable=self.sort_mode, value="child")
        child_radio.pack(side="left", padx=5)
        ToolTip(child_radio, "Sort files in each first-level subfolder.")

        deep_chk = ttk.Checkbutton(
            mode_frame,
            text="Deep Audit",
            variable=self.deep_audit
        )
        deep_chk.pack(side="left", padx=10)
        ToolTip(deep_chk, "If checked, recursively move misplaced files to their correct folders after sorting.")

        # Sort button
        sort_btn = ttk.Button(self.root, text="Sort Files", command=self._sort_files)
        sort_btn.pack(pady=10)
        ToolTip(sort_btn, "Start sorting files according to the selected options.")

        # Help button
        help_frame = ttk.Frame(self.root)
        help_frame.pack(fill="both", expand=False, padx=10, pady=5)
        help_btn = ttk.Button(help_frame, text="Help", command=self._show_help)
        help_btn.pack(side="right", anchor="se")
        ToolTip(help_btn, "Show help and usage instructions.")

    def _populate_mappings(self):
        """
        Populate the mapping combobox with available mapping files.
        """
        mappings_folder = MappingUtils.get_mappings_folder()
        mapping_files = MappingUtils.list_mapping_files(mappings_folder)
        self.mapping_combo['values'] = mapping_files
        if mapping_files:
            self.mapping_combo.current(0)
            self.mapping_path = os.path.join(mappings_folder, mapping_files[0])

    def _on_mapping_selected(self, event):
        """
        Update the selected mapping path when the user selects a mapping.
        """
        selected = self.mapping_combo.get()
        if selected:
            self.mapping_path = os.path.join(MappingUtils.get_mappings_folder(), selected)

    def _browse_directory(self):
        """
        Open a dialog for the user to select a directory to sort.
        """
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
            self.directory = directory

    def _open_mapping_editor(self):
        """
        Open the mapping editor window.
        """
        MappingEditor(self.root, self._populate_mappings)

    def _sort_files(self):
        """
        Perform the sorting operation based on user selections.
        """
        mapping_path = self.mapping_path
        directory = self.dir_entry.get()
        if not mapping_path or not os.path.isfile(mapping_path):
            show_error("Please select a valid mapping file.")
            return
        if not directory or not os.path.isdir(directory):
            show_error("Please select a valid directory to sort.")
            return

        try:
            sorter = FileSorter(mapping_path)
            mode = self.sort_mode.get()
            deep_audit = self.deep_audit.get()
            if mode == "single":
                sorter.sort_current_directory(directory)
                if deep_audit:
                    sorter.deep_audit_and_sort(directory)
            elif mode == "child":
                sorter.sort_first_level_subdirs(directory)
                if deep_audit:
                    for subdir in os.listdir(directory):
                        subdir_path = os.path.join(directory, subdir)
                        if os.path.isdir(subdir_path):
                            sorter.deep_audit_and_sort(subdir_path)
            else:
                show_error("Unknown sorting mode selected.")
                return
            messagebox.showinfo("Success", "Files sorted successfully!")
        except Exception as e:
            show_error(f"An error occurred during sorting:\n{e}")

def main():
    """
    Entry point for the GUI application.
    """
    root = tk.Tk()
    FileSorterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()