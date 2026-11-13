#!/usr/bin/env python3
import os
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk

WALLPAPER_DIR = os.path.expanduser("~/wall")
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp")

WALLPAPERS = sorted(
    f for f in os.listdir(WALLPAPER_DIR)
    if f.lower().endswith(IMAGE_EXTS)
)
THUMB_W, THUMB_H = 320, 180
BG       = "#0d0f14"
PANEL    = "#13161e"
ACCENT   = "#7aa2f7"
TEXT     = "#c0caf5"
SUBTEXT  = "#565f89"
BORDER   = "#1a1b26"
HOVER    = "#1e2030"
ACTIVE   = "#24283b"
FONT_H   = ("Inter", 13, "bold")
FONT_B   = ("Inter", 11)
FONT_S   = ("Inter", 9)


def apply_wallpaper(path: str) -> None:
    abs_path = os.path.abspath(path)

    try:
        subprocess.run(
            ["hyprctl", "hyprpaper", "preload", abs_path],
            check=True, capture_output=True
        )
        subprocess.run(
            ["hyprctl", "hyprpaper", "wallpaper", f",{abs_path}"],
            check=True, capture_output=True
        )
        subprocess.run(
            ["eww", "reload"],
            capture_output=True 
        )
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        subprocess.run(["swww", "img", abs_path], check=True, capture_output=True)
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    messagebox.showerror(
        "Nemas hyprland be",
    )


def on_plus(on_added):
    path = filedialog.askopenfilename(
        title="Select a wallpaper",
        initialdir=WALLPAPER_DIR,
        filetypes=[
            ("Images", ("*.jpg", "*.jpeg", "*.png", "*.webp")),
            ("All files", "*"),
        ],
    )
    if not path:
        return

    filename = os.path.basename(path)
    dest = os.path.join(WALLPAPER_DIR, filename)

    if os.path.abspath(path) != os.path.abspath(dest):
        shutil.copy(path, dest)

    if filename not in WALLPAPERS:
        WALLPAPERS.append(filename)
        on_added()


def on_remove(card, on_removed):
    if not messagebox.askyesno(
        "Remove wallpaper",
        f"Delete {card.filename} from {WALLPAPER_DIR}?"
    ):
        return
    try:
        os.remove(card.path)
    except OSError as exc:
        messagebox.showerror("Remove wallpaper", str(exc))
        return
    if card.filename in WALLPAPERS:
        WALLPAPERS.remove(card.filename)
    on_removed()


class WallCard(tk.Frame):
    def __init__(self, parent, index: int, filename: str, on_apply, on_removed, **kw):
        super().__init__(parent, bg=PANEL, bd=0, highlightthickness=1,
                         highlightbackground=BORDER, **kw)
        self.index    = index
        self.filename = filename
        self.on_apply = on_apply
        self.on_removed = on_removed
        self.path     = os.path.join(WALLPAPER_DIR, filename)
        self._active  = False
        self._img_ref = None

        self._build()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _build(self):
        thumb_frame = tk.Frame(self, bg=BORDER, width=THUMB_W, height=THUMB_H)
        thumb_frame.pack_propagate(False)
        thumb_frame.pack(padx=12, pady=(12, 6))

        self.thumb_label = tk.Label(thumb_frame, bg=BORDER, cursor="hand2")
        self.thumb_label.pack(fill="both", expand=True)
        self.thumb_label.bind("<Button-1>", lambda _: self._apply())
        self._load_thumbnail()

        name_row = tk.Frame(self, bg=PANEL)
        name_row.pack(fill="x", padx=12)

        idx_lbl = tk.Label(name_row, text=f"{self.index + 1:02d}",
                           font=FONT_S, bg=PANEL, fg=SUBTEXT)
        idx_lbl.pack(side="left")

        tk.Label(name_row, text=self.filename,
                 font=FONT_B, bg=PANEL, fg=TEXT,
                 anchor="w").pack(side="left", padx=(6, 0))

        self.btn = tk.Button(
            self, text="Apply",
            font=FONT_B, bg=ACTIVE, fg=TEXT,
            activebackground=ACCENT, activeforeground=BG,
            relief="flat", bd=0, cursor="hand2",
            padx=0, pady=6,
            command=self._apply
        )
        self.btn.pack(fill="x", padx=12, pady=(6, 12))

        self.x_btn = tk.Button(
            self, text="✕", font=FONT_S,
            bg=BORDER, fg=TEXT,
            activebackground="#f7768e", activeforeground=BG,
            relief="flat", bd=0, cursor="hand2",
            padx=6, pady=2,
            command=lambda: on_remove(self, self.on_removed)
        )
        self.x_btn.place(relx=1.0, x=-18, y=18, anchor="ne")
        self.x_btn.lift()

    def _load_thumbnail(self):
        if not os.path.isfile(self.path):
            self.thumb_label.config(text="[not found]", fg=SUBTEXT)
            return
        try:
            img = Image.open(self.path)
            img.thumbnail((THUMB_W, THUMB_H), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.thumb_label.config(image=photo, text="")
            self._img_ref = photo 
        except Exception as exc:
            self.thumb_label.config(text=f"[error: {exc}]", fg=SUBTEXT)

    def _apply(self):
        self.on_apply(self)

    def _on_enter(self, _=None):
        if not self._active:
            self.config(highlightbackground=SUBTEXT)

    def _on_leave(self, _=None):
        if not self._active:
            self.config(highlightbackground=BORDER)

    def set_active(self, active: bool):
        self._active = active
        if active:
            self.config(highlightbackground=ACCENT, highlightthickness=2)
            self.btn.config(text="✓ Active", bg=ACCENT, fg=BG,
                            activebackground=ACCENT, activeforeground=BG)
        else:
            self.config(highlightbackground=BORDER, highlightthickness=1)
            self.btn.config(text="Apply", bg=ACTIVE, fg=TEXT,
                            activebackground=ACCENT, activeforeground=BG)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wallpaper Switcher")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.bind("<Escape>", lambda _: self.destroy())
        self._cards: list[WallCard] = []
        self._active_card: WallCard | None = None
        self._active_name: str | None = None
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=24, pady=(20, 4))

        tk.Label(hdr, text="Wallpapers", font=("Inter", 18, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")
        tk.Button(hdr, text="+", font=("Inter", 16, "bold"),
                  bg=BG, fg=ACCENT,
                  activebackground=ACCENT, activeforeground=BG,
                  relief="flat", bd=0, cursor="hand2",
                  padx=8, pady=0,
                  command=lambda: on_plus(self._refresh)).pack(side="right")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=24, pady=(4, 16))

        wrap = tk.Frame(self, bg=BG)
        wrap.pack(fill="both", expand=True, padx=(20, 0), pady=(0, 20))

        self.canvas = tk.Canvas(wrap, bg=BG, highlightthickness=0,
                                width=1, height=1, yscrollincrement=40)
        scroll = tk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.grid_frame = tk.Frame(self.canvas, bg=BG)
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.grid_frame.bind(
            "<Configure>",
            lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.bind_all("<Button-4>", lambda _: self.canvas.yview_scroll(-1, "units"))
        self.bind_all("<Button-5>", lambda _: self.canvas.yview_scroll(1, "units"))

        self._populate()

        self.update_idletasks()
        self.canvas.config(width=self.grid_frame.winfo_reqwidth(),
                           height=min(self.grid_frame.winfo_reqheight(), 600))

        status_bar = tk.Frame(self, bg=PANEL, height=32)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)

        self.status_var = tk.StringVar(value="Select a wallpaper to apply it.")
        tk.Label(status_bar, textvariable=self.status_var,
                 font=FONT_S, bg=PANEL, fg=SUBTEXT,
                 anchor="w").pack(side="left", padx=14, pady=4)

        tk.Label(status_bar, text=WALLPAPER_DIR,
                 font=FONT_S, bg=PANEL, fg=BORDER,
                 anchor="e").pack(side="right", padx=14)

    def _populate(self):
        for card in self._cards:
            card.destroy()
        self._cards.clear()
        self._active_card = None

        cols = 3
        for i, name in enumerate(WALLPAPERS):
            row, col = divmod(i, cols)
            card = WallCard(self.grid_frame, i, name, self._on_apply, self._populate)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self._cards.append(card)
            if name == self._active_name:
                card.set_active(True)
                self._active_card = card

    def _refresh(self):
        self._populate()
        self.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def _on_apply(self, card: WallCard):
        if self._active_card:
            self._active_card.set_active(False)

        apply_wallpaper(card.path)
        card.set_active(True)
        self._active_card = card
        self._active_name = card.filename
        self.status_var.set(f"Applied: {card.filename}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
