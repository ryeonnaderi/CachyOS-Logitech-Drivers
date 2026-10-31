
#!/usr/bin/env python3

import re
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser

DEVICE = "singing-gundi"

BG = "#101113"
PANEL = "#1a1b1f"
PANEL_HI = "#292a30"
RED = "#e52332"
RED_HI = "#ff3545"
TEXT = "#f4f4f5"
MUTED = "#9698a1"
BORDER = "#303137"


def ratbag(*args):
    """Run ratbagctl and raise an error if the command fails."""
    result = subprocess.run(
        ["ratbagctl", DEVICE, *map(str, args)],
        capture_output=True,
        text=True,
        timeout=8,
    )

    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(error or "ratbagctl command failed")

    return result.stdout.strip()


def read_number(*args):
    output = ratbag(*args)
    match = re.search(r"\d+", output)

    if not match:
        raise RuntimeError(f"Unexpected response: {output}")

    return int(match.group())


class G403App:
    def __init__(self, root):
        self.root = root
        root.title("G403 CONTROL")
        root.geometry("820x720")
        root.minsize(700, 620)
        root.configure(bg=BG)

        # Performance
        self.dpi = tk.StringVar(value="800")
        self.rate = tk.StringVar(value="1000")

        # Lighting
        self.led = tk.StringVar(value="0")
        self.mode = tk.StringVar(value="cycle")
        self.color = "#ff253a"
        self.brightness = tk.IntVar(value=255)
        self.duration = tk.IntVar(value=8000)

        # Buttons
        self.button_index = tk.StringVar(value="5")
        self.button_kind = tk.StringVar(value="Special action")
        self.button_action = tk.StringVar(value="resolution-cycle-up")

        # Status
        self.status = tk.StringVar(value="Ready")

        self.build()
        self.refresh()
        self.read_button_action()

    def label(self, parent, text, size=10, color=TEXT, bold=False):
        return tk.Label(
            parent,
            text=text,
            bg=parent.cget("bg"),
            fg=color,
            font=("Sans", size, "bold" if bold else "normal"),
        )

    def button(self, parent, text, command, primary=False):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=RED if primary else PANEL_HI,
            fg=TEXT,
            activebackground=RED_HI,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=9,
            cursor="hand2",
            font=("Sans", 10, "bold"),
        )

    def card(self, parent):
        return tk.Frame(
            parent,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1,
        )

    def build(self):
        # Header
        header = tk.Frame(self.root, bg="#090a0b")
        header.pack(fill="x")

        self.label(header, "G 403 CONTROL", 19, RED, True).pack(
            side="left", padx=22, pady=18
        )

        self.label(
            header, "HERO GAMING MOUSE", 9, MUTED, True
        ).pack(side="right", padx=22)

        # Notebook styling
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TNotebook",
            background=BG,
            borderwidth=0,
        )
        style.configure(
            "TNotebook.Tab",
            background=PANEL,
            foreground=TEXT,
            padding=(16, 10),
            font=("Sans", 10, "bold"),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", RED)],
            foreground=[("selected", "white")],
        )
        style.configure(
            "TCombobox",
            fieldbackground=PANEL_HI,
            background=PANEL_HI,
            foreground=TEXT,
            arrowcolor=RED,
            padding=6,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", PANEL_HI)],
            foreground=[("readonly", TEXT)],
        )

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=20, pady=18)

        performance = tk.Frame(notebook, bg=BG)
        lighting = tk.Frame(notebook, bg=BG)
        buttons = tk.Frame(notebook, bg=BG)

        notebook.add(performance, text="  PERFORMANCE  ")
        notebook.add(lighting, text="  LIGHTING  ")
        notebook.add(buttons, text="  BUTTONS  ")

        self.build_performance(performance)
        self.build_lighting(lighting)
        self.build_buttons(buttons)

        # Footer
        footer = tk.Frame(self.root, bg="#090a0b")
        footer.pack(fill="x", side="bottom")

        tk.Label(
            footer,
            textvariable=self.status,
            bg="#090a0b",
            fg=MUTED,
            font=("Sans", 9),
        ).pack(side="left", padx=22, pady=13)

        self.button(
            footer, "REFRESH", self.refresh
        ).pack(side="right", padx=18, pady=7)

    # ---------------------------------------------------------
    # PERFORMANCE TAB
    # ---------------------------------------------------------

    def build_performance(self, parent):
        card = self.card(parent)
        card.pack(fill="x", pady=(0, 14))

        self.label(
            card, "SENSITIVITY / DPI", 11, RED, True
        ).pack(anchor="w", padx=20, pady=(18, 8))

        self.dpi_readout = self.label(
            card, "800 DPI", 28, TEXT, True
        )
        self.dpi_readout.pack(anchor="w", padx=20)

        dpi_row = tk.Frame(card, bg=PANEL)
        dpi_row.pack(fill="x", padx=20, pady=16)

        ttk.Combobox(
            dpi_row,
            textvariable=self.dpi,
            state="normal",
            values=[400, 800, 1200, 1600, 2400, 3200, 6400],
            width=15,
        ).pack(side="left")

        self.button(
            dpi_row, "APPLY DPI", self.apply_dpi, True
        ).pack(side="left", padx=10)

        self.label(
            card, "POLLING RATE", 11, RED, True
        ).pack(anchor="w", padx=20, pady=(10, 8))

        self.rate_readout = self.label(
            card, "1000 Hz", 28, TEXT, True
        )
        self.rate_readout.pack(anchor="w", padx=20)

        rate_row = tk.Frame(card, bg=PANEL)
        rate_row.pack(fill="x", padx=20, pady=16)

        ttk.Combobox(
            rate_row,
            textvariable=self.rate,
            state="readonly",
            values=[125, 250, 500, 1000],
            width=15,
        ).pack(side="left")

        self.button(
            rate_row, "APPLY RATE", self.apply_rate, True
        ).pack(side="left", padx=10)

        self.label(
            parent,
            "Settings are applied through ratbagctl.",
            9, MUTED,
        ).pack(anchor="w", pady=8)

    def refresh(self):
        try:
            dpi = read_number("dpi", "get")
            rate = read_number("rate", "get")

            self.dpi.set(str(dpi))
            self.rate.set(str(rate))

            self.dpi_readout.configure(text=f"{dpi:,} DPI")
            self.rate_readout.configure(text=f"{rate:,} Hz")

            self.status.set("DEVICE CONNECTED  •  Settings refreshed")

        except Exception as exc:
            self.status.set("Unable to read mouse settings")
            messagebox.showerror(
                "G403 connection error",
                str(exc),
                parent=self.root,
            )

    def apply_dpi(self):
        try:
            value = int(self.dpi.get())

            if not 100 <= value <= 25000:
                raise ValueError("DPI must be between 100 and 25000.")

            ratbag("dpi", "set", value)
            self.refresh()
            self.status.set(f"DPI set to {value}")

        except Exception as exc:
            messagebox.showerror(
                "DPI error", str(exc), parent=self.root
            )

    def apply_rate(self):
        try:
            value = int(self.rate.get())

            ratbag("rate", "set", value)
            self.refresh()
            self.status.set(f"Polling rate set to {value} Hz")

        except Exception as exc:
            messagebox.showerror(
                "Polling-rate error", str(exc), parent=self.root
            )

    # ---------------------------------------------------------
    # LIGHTING TAB
    # ---------------------------------------------------------

    def build_lighting(self, parent):
        card = self.card(parent)
        card.pack(fill="x")

        self.label(
            card, "RGB LIGHTING", 15, RED, True
        ).pack(anchor="w", padx=20, pady=(20, 5))

        self.label(
            card, "Configure either of the mouse's two LEDs.",
            10, MUTED,
        ).pack(anchor="w", padx=20, pady=(0, 16))

        self.label(
            card, "LED DEVICE", 9, MUTED, True
        ).pack(anchor="w", padx=20)

        ttk.Combobox(
            card,
            textvariable=self.led,
            values=["0", "1"],
            state="readonly",
            width=12,
        ).pack(anchor="w", padx=20, pady=(6, 16))

        self.label(
            card, "LIGHTING MODE", 9, MUTED, True
        ).pack(anchor="w", padx=20)

        ttk.Combobox(
            card,
            textvariable=self.mode,
            values=["on", "cycle", "breathing", "off"],
            state="readonly",
            width=18,
        ).pack(anchor="w", padx=20, pady=(6, 16))

        color_row = tk.Frame(card, bg=PANEL)
        color_row.pack(fill="x", padx=20, pady=(0, 14))

        self.label(
            color_row, "LED COLOR", 9, MUTED, True
        ).pack(side="left")

        self.color_swatch = tk.Label(
            color_row, bg=self.color, width=5, height=2
        )
        self.color_swatch.pack(side="left", padx=14)

        self.button(
            color_row, "CHOOSE COLOR", self.choose_color
        ).pack(side="left")

        self.label(
            card, "BRIGHTNESS", 9, MUTED, True
        ).pack(anchor="w", padx=20)

        tk.Scale(
            card,
            from_=0,
            to=255,
            variable=self.brightness,
            orient="horizontal",
            bg=PANEL,
            fg=TEXT,
            troughcolor="#3a3b42",
            activebackground=RED,
            highlightthickness=0,
            bd=0,
        ).pack(fill="x", padx=14, pady=(0, 12))

        self.label(
            card, "CYCLE / BREATHING DURATION (ms)", 9, MUTED, True
        ).pack(anchor="w", padx=20)

        tk.Scale(
            card,
            from_=100,
            to=10000,
            resolution=100,
            variable=self.duration,
            orient="horizontal",
            bg=PANEL,
            fg=TEXT,
            troughcolor="#3a3b42",
            activebackground=RED,
            highlightthickness=0,
            bd=0,
        ).pack(fill="x", padx=14, pady=(0, 12))

        self.button(
            card, "APPLY LIGHTING", self.apply_lighting, True
        ).pack(fill="x", padx=20, pady=(4, 20))

        self.label(
            parent,
            "Some lighting settings depend on the selected mode and LED.",
            9, MUTED,
        ).pack(anchor="w", pady=10)

    def choose_color(self):
        selected = colorchooser.askcolor(
            color=self.color,
            title="Choose G403 LED color",
            parent=self.root,
        )

        if selected and selected[1]:
            self.color = selected[1]
            self.color_swatch.configure(bg=self.color)

    def apply_lighting(self):
        led = self.led.get()
        mode = self.mode.get()
        color = self.color.lstrip("#")
        brightness = int(self.brightness.get())
        duration = int(self.duration.get())

        try:
            ratbag(
                "profile", "0", "led", led,
                "set", "mode", mode,
            )

            errors = []

            for setting, value in (
                ("color", color),
                ("brightness", brightness),
                ("duration", duration),
            ):
                try:
                    ratbag(
                        "profile", "0", "led", led,
                        "set", setting, value,
                    )
                except Exception as exc:
                    errors.append(f"{setting}: {exc}")

            if errors:
                messagebox.showwarning(
                    "Lighting partially applied",
                    "Some settings could not be applied:\n\n"
                    + "\n".join(errors),
                    parent=self.root,
                )
            else:
                messagebox.showinfo(
                    "G403 lighting",
                    f"LED {led} updated successfully.",
                    parent=self.root,
                )

            self.status.set(f"LED {led}: {mode}")

        except Exception as exc:
            messagebox.showerror(
                "Lighting error", str(exc), parent=self.root
            )

    # ---------------------------------------------------------
    # BUTTON MAPPING TAB
    # ---------------------------------------------------------

    def build_buttons(self, parent):
        card = self.card(parent)
        card.pack(fill="x")

        self.label(
            card, "BUTTON MAPPING", 15, RED, True
        ).pack(anchor="w", padx=20, pady=(20, 5))

        self.label(
            card,
            "Assign actions to your six configurable mouse buttons.",
            10, MUTED,
        ).pack(anchor="w", padx=20, pady=(0, 16))

        self.label(
            card, "CONFIGURABLE BUTTON", 9, MUTED, True
        ).pack(anchor="w", padx=20)

        self.button_selector = ttk.Combobox(
            card,
            textvariable=self.button_index,
            values=["0", "1", "2", "3", "4", "5"],
            state="readonly",
            width=16,
        )
        self.button_selector.pack(
            anchor="w", padx=20, pady=(6, 12)
        )
        self.button_selector.bind(
            "<<ComboboxSelected>>", self.read_button_action
        )

        self.current_action = self.label(
            card, "Current action: loading...", 10, TEXT
        )
        self.current_action.pack(
            anchor="w", padx=20, pady=(0, 15)
        )

        self.label(
            card, "ACTION TYPE", 9, MUTED, True
        ).pack(anchor="w", padx=20)

        self.kind_selector = ttk.Combobox(
            card,
            textvariable=self.button_kind,
            values=[
                "Mouse button",
                "Keyboard key",
                "Special action",
                "Disabled",
            ],
            state="readonly",
            width=20,
        )
        self.kind_selector.pack(
            anchor="w", padx=20, pady=(6, 12)
        )
        self.kind_selector.bind(
            "<<ComboboxSelected>>", self.update_action_choices
        )

        self.label(
            card, "ACTION", 9, MUTED, True
        ).pack(anchor="w", padx=20)

        self.action_selector = ttk.Combobox(
            card,
            textvariable=self.button_action,
            state="readonly",
            width=25,
        )
        self.action_selector.pack(
            anchor="w", padx=20, pady=(6, 16)
        )

        self.button(
            card, "APPLY BUTTON ACTION",
            self.apply_button_action, True,
        ).pack(fill="x", padx=20, pady=(0, 12))

        self.button(
            card, "READ CURRENT MAPPING",
            self.read_button_action,
        ).pack(fill="x", padx=20, pady=(0, 20))

        self.update_action_choices()

    def update_action_choices(self, event=None):
        kind = self.button_kind.get()

        if kind == "Mouse button":
            choices = [
                "button 1",
                "button 2",
                "button 3",
                "button 4",
                "button 5",
            ]

        elif kind == "Keyboard key":
            choices = [
                "KEY_E",
                "KEY_F",
                "KEY_Q",
                "KEY_R",
                "KEY_SPACE",
                "KEY_LEFTSHIFT",
                "KEY_LEFTCTRL",
                "KEY_TAB",
                "KEY_ESC",
                "KEY_ENTER",
                "KEY_1",
                "KEY_2",
                "KEY_3",
                "KEY_4",
            ]

        elif kind == "Special action":
            choices = [
                "resolution-cycle-up",
                "resolution-cycle-down",
            ]

        else:
            choices = ["disabled"]

        self.action_selector["values"] = choices

        if self.button_action.get() not in choices:
            self.button_action.set(choices[0])

    def read_button_action(self, event=None):
        try:
            index = int(self.button_index.get())
            result = ratbag(
                "button", str(index), "action", "get"
            )

            self.current_action.configure(
                text=f"Current action: {result}"
            )
            self.status.set(f"Read mapping for button {index}")

        except Exception as exc:
            messagebox.showerror(
                "Button mapping error",
                str(exc),
                parent=self.root,
            )

    def apply_button_action(self):
        index = int(self.button_index.get())
        kind = self.button_kind.get()
        action = self.button_action.get()

        try:
            if kind == "Mouse button":
                ratbag(
                    "button", str(index), "action", "set",
                    "button", action.split()[-1],
                )

            elif kind == "Keyboard key":
                ratbag(
                    "button", str(index), "action", "set",
                    "key", action,
                )

            elif kind == "Special action":
                ratbag(
                    "button", str(index), "action", "set",
                    "special", action,
                )

            else:
                ratbag(
                    "button", str(index), "action", "set",
                    "disabled",
                )

            self.read_button_action()
            self.status.set(f"Updated button {index}")

        except Exception as exc:
            messagebox.showerror(
                "Could not remap button",
                str(exc),
                parent=self.root,
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = G403App(root)
    root.mainloop()