import tkinter as tk
from tkinter import ttk

class PatternBuilder(tk.Toplevel):
    """
    A robust dialog to help users build filename patterns without knowing wildcards.
    """
    def __init__(self, master, on_pattern_ready):
        super().__init__(master)
        self.title("Pattern Builder")
        self.geometry("370x260")
        self.on_pattern_ready = on_pattern_ready

        self.var_starts = tk.StringVar()
        self.var_contains = tk.StringVar()
        self.var_ends = tk.StringVar()
        self.var_ext = tk.StringVar()
        self.current_pattern = ""

        self._build_widgets()

    def _build_widgets(self):
        ttk.Label(self, text="Build a filename pattern:").pack(pady=10)

        frm = ttk.Frame(self)
        frm.pack(padx=10, pady=5, fill="x")

        ttk.Label(frm, text="Starts with:").grid(row=0, column=0, sticky="e")
        ttk.Entry(frm, textvariable=self.var_starts, width=20).grid(row=0, column=1, sticky="w")

        ttk.Label(frm, text="Contains:").grid(row=1, column=0, sticky="e")
        ttk.Entry(frm, textvariable=self.var_contains, width=20).grid(row=1, column=1, sticky="w")

        ttk.Label(frm, text="Ends with:").grid(row=2, column=0, sticky="e")
        ttk.Entry(frm, textvariable=self.var_ends, width=20).grid(row=2, column=1, sticky="w")

        ttk.Label(frm, text="Extension:").grid(row=3, column=0, sticky="e")
        ttk.Entry(frm, textvariable=self.var_ext, width=20).grid(row=3, column=1, sticky="w")
        ttk.Label(frm, text="(e.g. pdf, docx)").grid(row=3, column=2, sticky="w")

        self.pattern_preview = ttk.Label(self, text="Pattern: *")
        self.pattern_preview.pack(pady=10)

        for var in (self.var_starts, self.var_contains, self.var_ends, self.var_ext):
            var.trace_add("write", self._update_preview)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Use Pattern", command=self._use_pattern).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

        self._update_preview()

    def _update_preview(self, *args):
        starts = self.var_starts.get()
        contains = self.var_contains.get()
        ends = self.var_ends.get()
        ext = self.var_ext.get().lstrip(".")

        pattern = ""

        # Start
        if starts:
            pattern += starts

        # Contains (can be multiple, comma-separated)
        contains_parts = [c.strip() for c in contains.split(",") if c.strip()]
        for c in contains_parts:
            if not pattern.endswith("*") and pattern:
                pattern += "*"
            pattern += c
            pattern += "*"

        # If no contains, but starts and ends are set, add wildcard between
        if not contains_parts and starts and ends:
            if not pattern.endswith("*"):
                pattern += "*"

        # Ends with
        if ends:
            if pattern.endswith("*"):
                pattern = pattern[:-1]
            pattern += ends

        # Extension
        if ext:
            if pattern.endswith("*"):
                pattern = pattern[:-1]
            if not ext.startswith("."):
                pattern += f".{ext}"
            else:
                pattern += ext

        # If nothing is set, match everything
        if not (starts or contains_parts or ends or ext):
            pattern = "*"

        self.pattern_preview.config(text=f"Pattern: {pattern}")
        self.current_pattern = pattern

    def _use_pattern(self):
        self.on_pattern_ready(self.current_pattern)
        self.destroy()