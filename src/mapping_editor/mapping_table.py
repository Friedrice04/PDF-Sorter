import tkinter as tk
from tkinter import ttk

class MappingTable(ttk.Treeview):
    """
    A custom Treeview widget to display and manage mapping rules.
    Handles the start of drag-and-drop operations.
    """
    def __init__(self, master, on_item_drag, **kwargs):
        super().__init__(master, columns=("name", "phrase", "destination"), show="headings", **kwargs)
        self.heading("name", text="Rule Name")
        self.heading("phrase", text="Phrase / Keyword")
        self.heading("destination", text="Destination Folder")
        self.column("name", width=200, stretch=tk.NO, anchor="w")
        self.column("phrase", width=250, stretch=tk.YES, anchor="w")
        self.column("destination", width=250, stretch=tk.YES, anchor="w")

        self.on_item_drag = on_item_drag
        self._dragged_item = None

        self.bind("<ButtonPress-1>", self._on_drag_start)

    def _on_drag_start(self, event):
        """Identifies the item under the cursor and initiates the drag."""
        item_id = self.identify_row(event.y)
        if item_id:
            # Get the phrase (the unique key) from the selected row's values
            self._dragged_item = self.item(item_id, "values")[1] # Index 1 is the phrase
            # Call the action handler with only the required argument
            self.on_item_drag(self._dragged_item)

    def refresh(self, mappings):
        """Clears and repopulates the table with the given mapping data."""
        # Clear all existing items from the table
        for item in self.get_children():
            self.delete(item)
        # Insert the new mapping rules
        if mappings:
            for phrase, rule in mappings.items():
                name = rule.get("name", "")
                dest = rule.get("dest", "")
                self.insert("", "end", values=(name, phrase, dest))