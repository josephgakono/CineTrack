import tkinter as tk
from tkinter import messagebox, ttk

from database import authenticate_user, init_database, register_user


COLORS = {
    "bg": "#12151f",
    "panel": "#1b2030",
    "muted": "#8f98ad",
    "text": "#f5f7fb",
    "accent": "#f5c451",
}


class CineTrackApp(tk.Tk):
    def __init__(self):
        super().__init__()
        init_database()
        self.user = None
        self.title("CineTrack")
        self.geometry("980x620")
        self.minsize(860, 540)
        self.configure(bg=COLORS["bg"])
        self._style_widgets()
        self._build_shell()
        self.show_login()

    def _style_widgets(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=COLORS["bg"])
        style.configure("Panel.TFrame", background=COLORS["panel"])
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=("Segoe UI", 10))
        style.configure("Muted.TLabel", foreground=COLORS["muted"])
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 22))
        style.configure("Card.TLabel", background=COLORS["panel"], foreground=COLORS["text"])
        style.configure("TEntry", fieldbackground="#f6f7fb", padding=8)
        style.configure("TButton", padding=(14, 8), font=("Segoe UI Semibold", 10))
        style.configure("Accent.TButton", background=COLORS["accent"], foreground="#16120a")

    def _build_shell(self):
        self.sidebar = ttk.Frame(self, style="Panel.TFrame", width=210)
        self.sidebar.pack(side="left", fill="y")
        self.content = ttk.Frame(self, padding=28)
        self.content.pack(side="right", fill="both", expand=True)
        tk.Label(self.sidebar, text="CineTrack", bg=COLORS["panel"], fg=COLORS["accent"], font=("Segoe UI Semibold", 24)).pack(anchor="w", padx=22, pady=(28, 4))
        tk.Label(self.sidebar, text="Movie taste, saved neatly.", bg=COLORS["panel"], fg=COLORS["muted"], font=("Segoe UI", 9)).pack(anchor="w", padx=22, pady=(0, 28))
        self.nav = ttk.Frame(self.sidebar, style="Panel.TFrame")
        self.nav.pack(fill="x", padx=16)

    def _set_nav(self):
        for child in self.nav.winfo_children():
            child.destroy()
        if not self.user:
            return
        tk.Button(self.nav, text="Sign out", command=self.show_login, bg=COLORS["panel"], fg=COLORS["text"], relief="flat", anchor="w", padx=14, pady=10).pack(fill="x")

    def _clear(self):
        for child in self.content.winfo_children():
            child.destroy()

    def _page_title(self, title, subtitle):
        ttk.Label(self.content, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.content, text=subtitle, style="Muted.TLabel").pack(anchor="w", pady=(2, 22))

    def show_login(self):
        self.user = None
        self._set_nav()
        self._clear()
        self._page_title("Welcome back", "Sign in or create a small local account for your movie lists.")
        card = ttk.Frame(self.content, style="Panel.TFrame", padding=26)
        card.pack(anchor="w", fill="x")
        username, password = tk.StringVar(), tk.StringVar()
        for label, var, hidden in (("Username", username, False), ("Password", password, True)):
            ttk.Label(card, text=label, style="Card.TLabel").pack(anchor="w")
            ttk.Entry(card, textvariable=var, show="*" if hidden else "").pack(fill="x", pady=(5, 14))

        def login():
            user = authenticate_user(username.get(), password.get())
            if not user:
                messagebox.showerror("Login failed", "Check the username and password.")
                return
            self.user = user
            self._set_nav()
            self._page_title("Signed in", f"Hello, {self.user['username']}.")

        def register():
            try:
                self.user = {"id": register_user(username.get(), password.get()), "username": username.get().strip()}
                self._set_nav()
                self._page_title("Account ready", f"Hello, {self.user['username']}.")
            except ValueError as exc:
                messagebox.showerror("Registration failed", str(exc))

        row = ttk.Frame(card, style="Panel.TFrame")
        row.pack(anchor="e", pady=(4, 0))
        ttk.Button(row, text="Create account", command=register).pack(side="left", padx=(0, 10))
        ttk.Button(row, text="Sign in", style="Accent.TButton", command=login).pack(side="left")


if __name__ == "__main__":
    CineTrackApp().mainloop()
