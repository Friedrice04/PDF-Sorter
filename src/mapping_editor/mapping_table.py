import tkinter as tk
from tkinter import ttk

class MappingTable(ttk.Treeview):
    """
    A custom Treeview widget to display and manage mapping rules.
    Handles the start of drag-and-drop operations.
    """
    def __init__(self, master, on_item_drag, **kwargs):
        super().__init__(master, columns=("phrase", "destination"), show="headings", **kwargs)
        self.heading("phrase", text="Phrase / Keyword")
        self.heading("destination", text="Destination Folder")
        self.column("phrase", width=250, stretch=tk.YES)
        self.column("destination", width=250, stretch=tk.YES)

        self.on_item_drag = on_item_drag
        self._dragged_item = None

        self.bind("<ButtonPress-1>", self._on_drag_start)

    def _on_drag_start(self, event):
        """Identifies the item under the cursor and initiates the drag."""
        item_id = self.identify_row(event.y)
        if item_id:
            # Get the phrase (the unique key) from the selected row
            self._dragged_item = self.item(item_id, "values")[0]
            # Call the action handler with only the required argument
            self.on_item_drag(self._dragged_item)

    def refresh(self, mappings):
        """Clears and repopulates the table with the given mapping data."""
        # Clear all existing items from the table
        for item in self.get_children():
            self.delete(item)
        # Insert the new mapping rules
        if mappings:
            for phrase, dest in mappings.items():
                self.insert("", "end", values=(phrase, dest))