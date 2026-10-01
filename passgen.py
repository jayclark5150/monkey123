"""Monkey123 — cross-platform desktop password / passphrase generator (Tkinter)."""

import tkinter as tk
from tkinter import ttk

import generator as gen

__version__ = "1.2.0"

SEPARATORS = {
    "Hyphen ( - )": "-",
    "Space (   )": " ",
    "Period ( . )": ".",
    "Underscore ( _ )": "_",
    "Comma ( , )": ",",
    "None": "",
    "Custom": None,
}

# Meter is full at 128 bits; colors match gen.strength_label() thresholds.
METER_MAX_BITS = 128
STRENGTH_COLORS = {
    "Weak": "#d32f2f",
    "Fair": "#f57c00",
    "Strong": "#7cb342",
    "Very strong": "#2e7d32",
}


class App(ttk.Frame):
    def __init__(self, root: tk.Tk):
        super().__init__(root, padding=16)
        self.root = root
        self.words = gen.load_wordlist()
        self.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # --- Mode ---
        self.mode = tk.StringVar(value="password")
        mode_row = ttk.Frame(self)
        mode_row.grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(mode_row, text="Password", value="password", variable=self.mode,
                        command=self._on_mode).pack(side="left", padx=(0, 12))
        ttk.Radiobutton(mode_row, text="Passphrase", value="passphrase", variable=self.mode,
                        command=self._on_mode).pack(side="left")

        # --- Output ---
        self.output = tk.StringVar()
        out_row = ttk.Frame(self)
        out_row.grid(row=1, column=0, sticky="ew", pady=12)
        out_row.columnconfigure(0, weight=1)
        entry = ttk.Entry(out_row, textvariable=self.output, font=("Courier", 14), state="readonly")
        entry.grid(row=0, column=0, sticky="ew", ipady=4)
        ttk.Button(out_row, text="Copy", command=self.copy).grid(row=0, column=1, padx=(8, 0))

        self.info = tk.StringVar()
        ttk.Label(self, textvariable=self.info).grid(row=2, column=0, sticky="w")

        # --- Option panels ---
        self.pw_frame = self._build_password_options()
        self.pp_frame = self._build_passphrase_options()

        # --- Actions ---
        actions = ttk.Frame(self)
        actions.grid(row=4, column=0, sticky="ew", pady=(12, 0))
        actions.columnconfigure(1, weight=1)
        ttk.Label(actions, text="Strength:").grid(row=0, column=0, sticky="w")
        self.meter = tk.Canvas(actions, height=14, highlightthickness=0, background="#e0e0e0")
        self.meter.grid(row=0, column=1, sticky="ew", padx=8)
        self.meter.bind("<Configure>", lambda _e: self._draw_meter())
        self.meter_label = ttk.Label(actions, width=11)
        self.meter_label.grid(row=0, column=2, sticky="w")
        ttk.Button(actions, text="Generate", command=self.generate).grid(row=0, column=3, padx=(8, 0))
        self.bits = 0.0

        self.status = tk.StringVar()
        ttk.Label(self, textvariable=self.status, foreground="#b00020").grid(row=5, column=0, sticky="w")

        root.bind("<Return>", lambda _e: self.generate())
        self._on_mode()

    # ---------- UI builders ----------
    def _build_password_options(self):
        f = ttk.LabelFrame(self, text="Password options", padding=12)
        self.length = tk.IntVar(value=16)
        ttk.Label(f, text="Character count:").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(f, from_=4, to=128, textvariable=self.length, width=6,
                    command=self.generate).grid(row=0, column=1, sticky="w", padx=8)

        self.use_lower = tk.BooleanVar(value=True)
        self.use_upper = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        for i, (label, var) in enumerate([
            ("Lowercase (a-z)", self.use_lower),
            ("Uppercase (A-Z)", self.use_upper),
            ("Numbers (0-9)", self.use_digits),
            ("Special characters (!@#$...)", self.use_symbols),
        ]):
            ttk.Checkbutton(f, text=label, variable=var, command=self.generate).grid(
                row=1 + i, column=0, columnspan=3, sticky="w", pady=1)
        return f

    def _build_passphrase_options(self):
        f = ttk.LabelFrame(self, text="Passphrase options", padding=12)
        self.word_count = tk.IntVar(value=5)
        ttk.Label(f, text="Word count:").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(f, from_=3, to=20, textvariable=self.word_count, width=6,
                    command=self.generate).grid(row=0, column=1, sticky="w", padx=8)

        ttk.Label(f, text="Word separator:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.sep_choice = tk.StringVar(value="Hyphen ( - )")
        combo = ttk.Combobox(f, textvariable=self.sep_choice, values=list(SEPARATORS),
                             state="readonly", width=16)
        combo.grid(row=1, column=1, sticky="w", padx=8, pady=(6, 0))
        combo.bind("<<ComboboxSelected>>", lambda _e: self._on_sep())
        self.custom_sep = tk.StringVar(value="+")
        self.custom_entry = ttk.Entry(f, textvariable=self.custom_sep, width=6)
        self.custom_entry.grid(row=1, column=2, sticky="w", pady=(6, 0))
        self.custom_sep.trace_add("write", lambda *_: self.generate())

        self.capitalize = tk.BooleanVar(value=True)
        self.pp_number = tk.BooleanVar(value=True)
        self.pp_symbol = tk.BooleanVar(value=False)
        for i, (label, var) in enumerate([
            ("Capitalize words", self.capitalize),
            ("Include a number", self.pp_number),
            ("Include a special character", self.pp_symbol),
        ]):
            ttk.Checkbutton(f, text=label, variable=var, command=self.generate).grid(
                row=2 + i, column=0, columnspan=3, sticky="w", pady=1)
        return f

    # ---------- Behaviour ----------
    def _on_mode(self):
        if self.mode.get() == "password":
            self.pp_frame.grid_remove()
            self.pw_frame.grid(row=3, column=0, sticky="ew")
        else:
            self.pw_frame.grid_remove()
            self.pp_frame.grid(row=3, column=0, sticky="ew")
            self._on_sep(regenerate=False)
        self.generate()

    def _on_sep(self, regenerate=True):
        if self.sep_choice.get() == "Custom":
            self.custom_entry.grid()
        else:
            self.custom_entry.grid_remove()
        if regenerate:
            self.generate()

    def _separator(self):
        sep = SEPARATORS[self.sep_choice.get()]
        return self.custom_sep.get() if sep is None else sep

    def generate(self):
        self.status.set("")
        try:
            if self.mode.get() == "password":
                result, bits = gen.generate_password(
                    length=self.length.get(),
                    lower=self.use_lower.get(), upper=self.use_upper.get(),
                    digits=self.use_digits.get(), symbols=self.use_symbols.get())
            else:
                result, bits = gen.generate_passphrase(
                    self.words, count=self.word_count.get(), separator=self._separator(),
                    capitalize=self.capitalize.get(),
                    add_number=self.pp_number.get(), add_symbol=self.pp_symbol.get())
        except (ValueError, tk.TclError) as e:
            self.status.set(str(e) if isinstance(e, ValueError) else "Enter a valid number.")
            return
        self.output.set(result)
        self.bits = bits
        self._draw_meter()
        self.info.set(f"{len(result)} characters  ·  ~{bits:.0f} bits entropy")

    def _draw_meter(self):
        label = gen.strength_label(self.bits)
        color = STRENGTH_COLORS[label]
        width = self.meter.winfo_width()
        fill = width * min(self.bits, METER_MAX_BITS) / METER_MAX_BITS
        self.meter.delete("all")
        self.meter.create_rectangle(0, 0, fill, self.meter.winfo_height(), fill=color, width=0)
        self.meter_label.configure(text=label, foreground=color)

    def copy(self):
        value = self.output.get()
        if value:
            self.root.clipboard_clear()
            self.root.clipboard_append(value)
            self.status.set("")
            self.info.set(self.info.get().split("  ·  Copied")[0] + "  ·  Copied!")


def main():
    # className sets the Linux WM_CLASS so the dock matches the .desktop launcher.
    root = tk.Tk(className="Monkey123")
    root.title("Monkey123")
    try:
        root.iconphoto(True, tk.PhotoImage(file=gen.resource_dir() / "assets" / "icon.png"))
    except tk.TclError:
        pass  # Icon is cosmetic; run without it if the file is missing.
    root.minsize(460, 360)
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
