import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

from src.utils import ToolTip
from src import utils

class MappingEditor(tk.Toplevel):
    """
    A window for editing file sorting mappings.
    """
    def __init__(self, master, on_save_callback=None):
        super().__init__(master)
        self.title("Mapping Editor")
        self.geometry("700x400")
        self.on_save_callback = on_save_callback
        self.mappings = {}  # pattern: destination
        self.mapping_path = None

        self._build_widgets()
        # Don't load mappings until a file is selected

    def _build_widgets(self):
        # --- Mapping file selection ---
        file_frame = ttk.Frame(self)
        file_frame.pack(fill="x", padx=10, pady=(10, 0))

        self.mapping_file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.mapping_file_var, state="readonly", width=60)
        file_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ToolTip(file_entry, "Currently selected mapping JSON file.")

        select_btn = ttk.Button(file_frame, text="Select Mapping File...", command=self._select_mapping_file)
        select_btn.pack(side="left")
        ToolTip(select_btn, "Choose a mapping JSON file to edit.")

        # Main frame for list and buttons
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Listbox for mapping rules
        self.mapping_list = tk.Listbox(main_frame, height=15)
        self.mapping_list.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=0)
        ToolTip(self.mapping_list, "List of pattern-to-folder mappings.")

        # Vertical button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side="left", fill="y")

        add_btn = ttk.Button(button_frame, text="Add", command=self._add_rule)
        add_btn.pack(fill="x", pady=(0, 5))
        ToolTip(add_btn, "Add a new pattern mapping.")

        edit_btn = ttk.Button(button_frame, text="Edit", command=self._edit_rule)
        edit_btn.pack(fill="x", pady=(0, 5))
        ToolTip(edit_btn, "Edit the selected mapping.")

        remove_btn = ttk.Button(button_frame, text="Remove", command=self._remove_rule)
        remove_btn.pack(fill="x", pady=(0, 5))
        ToolTip(remove_btn, "Remove the selected mapping.")

        move_up_btn = ttk.Button(button_frame, text="Move Up", command=self._move_up)
        move_up_btn.pack(fill="x", pady=(0, 5))
        ToolTip(move_up_btn, "Move the selected mapping up.")

        move_down_btn = ttk.Button(button_frame, text="Move Down", command=self._move_down)
        move_down_btn.pack(fill="x", pady=(0, 5))
        ToolTip(move_down_btn, "Move the selected mapping down.")

        # Save and Cancel at the bottom
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", padx=10, pady=(0, 10))

        save_btn = ttk.Button(bottom_frame, text="Save", command=self._save)
        save_btn.pack(side="right", padx=(5, 0))
        ToolTip(save_btn, "Save changes to the mapping file.")

        cancel_btn = ttk.Button(bottom_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side="right")
        ToolTip(cancel_btn, "Cancel and close the editor.")

    def _select_mapping_file(self):
        """
        Open a file dialog for the user to select a mapping JSON file.
        """
        file_path = filedialog.askopenfilename(
            title="Select Mapping JSON File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if file_path:
            self.mapping_path = file_path
            self.mapping_file_var.set(file_path)
            self._load_mappings()

    def _load_mappings(self):
        """
        Load mappings from the selected mapping file.
        """
        if self.mapping_path and utils.MappingUtils.is_valid_mapping_file(self.mapping_path):
            self.mappings = utils.MappingUtils.load_mapping(self.mapping_path)
            self._refresh_listbox()
        else:
            self.mappings = {}
            self.mapping_list.delete(0, tk.END)

    def _refresh_listbox(self):
        self.mapping_list.delete(0, tk.END)
        for pattern, dest in self.mappings.items():
            self.mapping_list.insert(tk.END, f"{pattern}  →  {dest}")

    def _add_rule(self):
        pattern = simpledialog.askstring("Add Pattern", "Enter the pattern (e.g. *.pdf):", parent=self)
        if not pattern:
            return
        if pattern in self.mappings:
            messagebox.showwarning("Duplicate Pattern", "This pattern already exists.")
            return
        dest = filedialog.askdirectory(title="Select Destination Folder")
        if not dest:
            return
        self.mappings[pattern] = dest
        self._refresh_listbox()

    def _edit_rule(self):
        selection = self.mapping_list.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a mapping to edit.")
            return
        index = selection[0]
        pattern = list(self.mappings.keys())[index]
        dest = self.mappings[pattern]
        new_pattern = simpledialog.askstring("Edit Pattern", "Edit the pattern:", initialvalue=pattern, parent=self)
        if not new_pattern:
            return
        if new_pattern != pattern and new_pattern in self.mappings:
            messagebox.showwarning("Duplicate Pattern", "This pattern already exists.")
            return
        new_dest = filedialog.askdirectory(title="Select Destination Folder", initialdir=dest)
        if not new_dest:
            return
        del self.mappings[pattern]
        self.mappings[new_pattern] = new_dest
        self._refresh_listbox()

    def _remove_rule(self):
        selection = self.mapping_list.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a mapping to remove.")
            return
        index = selection[0]
        pattern = list(self.mappings.keys())[index]
        del self.mappings[pattern]
        self._refresh_listbox()

    def _move_up(self):
        selection = self.mapping_list.curselection()
        if not selection or selection[0] == 0:
            return
        index = selection[0]
        keys = list(self.mappings.keys())
        key = keys[index]
        keys.insert(index - 1, keys.pop(index))
        self.mappings = {k: self.mappings[k] for k in keys}
        self._refresh_listbox()
        self.mapping_list.selection_set(index - 1)

    def _move_down(self):
        selection = self.mapping_list.curselection()
        if not selection or selection[0] == len(self.mappings) - 1:
            return
        index = selection[0]
        keys = list(self.mappings.keys())
        key = keys[index]
        keys.insert(index + 1, keys.pop(index))
        self.mappings = {k: self.mappings[k] for k in keys}
        self._refresh_listbox()
        self.mapping_list.selection_set(index + 1)

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