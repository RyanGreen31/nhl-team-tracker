"""
Reusable Tkinter pieces: colors, fonts, buttons, cards, star ratings, scroll area.
"""

import math
import time
import tkinter as tk
from tkinter import font as tkfont

COLORS = {
    "navy": "#0b2545",
    "navy_hover": "#163a66",
    "red": "#c8102e",
    "red_hover": "#a00d25",
    "bg": "#eaf2fb",
    "card": "#ffffff",
    "border": "#d6dee8",
    "text": "#1b2733",
    "muted": "#5f6b7a",
    "gold": "#d4a017",
    "star_empty": "#d2d8df",
    "green_bg": "#e8f6ea",
    "green_border": "#9fd3a8",
    "green_text": "#1e6b2e",
    "error_bg": "#fdecec",
    "error_border": "#f0a3a3",
    "error_text": "#a00d25",
    "highlight": "#fff8e1",
    "focus": "#4a8fe0",
    "link": "#1554a5",
}

FONTS = {}

def setup_fonts(root):
    family = "Segoe UI" if "Segoe UI" in tkfont.families(root) else "Helvetica"
    FONTS.update({
        "body": (family, 11),
        "bold": (family, 11, "bold"),
        "small": (family, 10),
        "h1": (family, 20, "bold"),
        "h2": (family, 12, "bold"),
        "button": (family, 11, "bold"),
        "button_sm": (family, 10, "bold"),
    })

# Buttons
BUTTON_STYLES = {
    "primary": (COLORS["red"], "white", COLORS["red_hover"], COLORS["red"]),
    "dark": (COLORS["navy"], "white", COLORS["navy_hover"], COLORS["navy"]),
    "outline": ("white", COLORS["navy"], "#f1f5fa", COLORS["navy"]),
    "danger": ("white", COLORS["red"], COLORS["error_bg"], COLORS["red"]),
    "nav": ("white", COLORS["navy"], "#dbe6f3", "white"),
    "nav_active": (COLORS["navy"], "white", COLORS["navy_hover"], "white"),
    "link": (None, COLORS["link"], None, None),
}

class AppButton(tk.Label):
    def __init__(self, parent, text, command, style="primary", small=False, **kwargs):
        bg, fg, hover, border = BUTTON_STYLES[style]
        parent_bg = parent.cget("bg")
        if style == "link":
            bg, hover, border = parent_bg, parent_bg, parent_bg
        super().__init__(
            parent, text=text, bg=bg, fg=fg, cursor="hand2", 
            font=FONTS["button_sm" if small else "button"], 
            padx=10 if small else 16, pady=3 if small else 8, 
            highlightthickness=2, highlightbackground=border, highlightcolor=COLORS["focus"], 
            takefocus=1, **kwargs, 
        )
        if style == "link":
            self.configure(font=FONTS["bold"] + ("underline",), padx=2, pady=2)
        self.command = command
        self.normal_bg, self.hover_bg = bg, hover
        self.bind("<Enter>", lambda e: self.configure(bg=self.hover_bg))
        self.bind("<Leave>", lambda e: self.configure(bg=self.normal_bg))
        self.bind("<Button-1>", self.invoke)
        self.bind("<Return>", self.invoke)
        self.bind("<space>", self.invoke)

    def invoke(self, event=None):
        # Remember when the user clicked, show how fast app responded
        root = self.winfo_toplevel()
        root.click_time = time.perf_counter()
        self.command()
        root.click_time = None
        return "break"

# Layout helpers
def card(parent, title=None, pack=True):
    frame = tk.Frame(parent, bg=COLORS["card"], highlightthickness=1,
                     highlightbackground=COLORS["border"], padx=14, pady=10)
    if pack:
        frame.pack(fill="x", pady=(0, 10))
    if title:
        tk.Label(frame, text=title, font=FONTS["h2"], fg=COLORS["navy"],
                 bg=COLORS["card"], anchor="w").pack(fill="x", pady=(0, 6))
    return frame

def text(parent, value, style="body", color=None, **kwargs):
    kwargs.setdefault("anchor", "w")
    kwargs.setdefault("justify", "left")
    return tk.Label(parent, text=value, font=FONTS[style], bg=parent.cget("bg"),
                    fg=color or COLORS["text"], **kwargs)

def banner(parent, message, kind="success"):
    """Green success or red error message bar."""
    bg, border, fg = {
        "success": (COLORS["green_bg"], COLORS["green_border"], COLORS["green_text"]),
        "error": (COLORS["error_bg"], COLORS["error_border"], COLORS["error_text"]),
    }[kind]
    frame = tk.Frame(parent, bg=bg, highlightthickness=1, highlightbackground=border,
                     padx=12, pady=8)
    label = tk.Label(frame, text=message, bg=bg, fg=fg, font=FONTS["body"],
                     anchor="w", justify="left", wraplength=820)
    label.pack(side="left", fill="x", expand=True)
    frame.label = label
    return frame

# Star rating
def _star_points(cx, cy, outer, inner):
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        radius = outer if i % 2 == 0 else inner
        points.append((cx + radius * math.cos(angle), cy - radius * math.sin(angle)))
    return points

def _left_half(points, cx):
    """Clip a polygon to the part left of the vertical line x = cx."""
    result = []
    for i, (x1, y1) in enumerate(points):
        x2, y2 = points[(i + 1) % len(points)]
        in1, in2 = x1 <= cx, x2 <= cx
        if in1:
            result.append((x1, y1))
        if in1 != in2:
            t = (cx - x1) / (x2 - x1)
            result.append((cx, y1 + t * (y2 - y1)))
    return result

def _flat(points):
    return [coord for point in points for coord in point]

class StarRating(tk.Canvas):
    """
    Five stars that can show half stars.
    interactive = True turns it into a picker: click the left half of a star for 
    a half star, the right half for a full star. Arrow keys change it by 0.5.
    """

    def __init__(self, parent, value=0, size=18, interactive=False, on_change=None):
        self.size = size
        width = size * 5 + 4
        super().__init__(parent, width=width, height=size + 4, bg=parent.cget("bg"),
                         highlightthickness=2 if interactive else 0,
                         highlightbackground=parent.cget("bg"),
                         highlightcolor=COLORS["focus"], takefocus=1 if interactive else 0)
        self.value = float(value or 0)
        self.on_change = on_change
        self.draw(self.value)
        if interactive:
            self.configure(cursor="hand2")
            self.bind("<Motion>", lambda e: self.draw(self.value_at(e.x)))
            self.bind("<Leave>", lambda e: self.draw(self.value))
            self.bind("<Button-1>", lambda e: (self.focus_set(), self.set(self.value_at(e.x))))
            self.bind("<Right>", lambda e: self.set(self.value + 0.5))
            self.bind("<Up>", lambda e: self.set(self.value + 0.5))
            self.bind("<Left>", lambda e: self.set(self.value - 0.5))
            self.bind("<Down>", lambda e: self.set(self.value - 0.5))

    def value_at(self, x):
        x = max(0, min(self.size * 5 - 0.01, x - 2))
        index = int(x // self.size)
        left_half = (x - index * self.size) < self.size / 2
        return index + (0.5 if left_half else 1)

    def set(self, value):
        self.value = max(0.0, min(5.0, round(value * 2) / 2))
        self.draw(self.value)
        if self.on_change:
            self.on_change(self.value)

    def draw(self, value):
        self.delete("all")
        outer, inner = self.size * 0.48, self.size * 0.2
        for i in range(5):
            cx, cy = 2 + self.size * i + self.size / 2, 2 + self.size / 2
            points = _star_points(cx, cy, outer, inner)
            fill = max(0.0, min(1.0, value - i))
            self.create_polygon(_flat(points), fill=COLORS["star_empty"], outline="")
            if fill >= 1:
                self.create_polygon(_flat(points), fill=COLORS["gold"], outline="")
            elif fill >= 0.5:
                self.create_polygon(_flat(_left_half(points, cx)), fill=COLORS["gold"], outline="")

# Scroll area
class ScrollFrame(tk.Frame):
    def __init__(self, parent, height=300, bg=None):
        bg = bg or COLORS["card"]
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, height=height, bg=bg, highlightthickness=0)
        bar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(window, width=e.width))
        self.canvas.configure(yscrollcommand=bar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y")
        # Mouse wheel scrolls only while the pointer is over this area
        self.bind("<Enter>", self._bind_wheel)
        self.bind("<Leave>", self._unbind_wheel)

    def _bind_wheel(self, _event):
        self.bind_all("<MouseWheel>", self._on_wheel)
        self.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _unbind_wheel(self, _event):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")

    def _on_wheel(self, event):
        step = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(step, "units")
