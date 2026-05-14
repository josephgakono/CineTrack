import tkinter as tk
from tkinter import messagebox, ttk

from api import search_movie
from database import (
    add_favorite,
    authenticate_user,
    init_database,
    list_favorites,
    list_watch_history,
    mark_watched,
    register_user,
)


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
        self.current_movie = None
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
        style.configure("Treeview", rowheight=30, background="#f7f8fb", fieldbackground="#f7f8fb")
        style.configure("Treeview.Heading", font=("Segoe UI Semibold", 10))

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
        for text, command in (("Search", self.show_search), ("Library", self.show_library), ("Sign out", self.show_login)):
            tk.Button(self.nav, text=text, command=command, bg=COLORS["panel"], fg=COLORS["text"], relief="flat", anchor="w", padx=14, pady=10).pack(fill="x", pady=3)

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
            self.show_search()

        def register():
            try:
                self.user = {"id": register_user(username.get(), password.get()), "username": username.get().strip()}
                self._set_nav()
                self.show_search()
            except ValueError as exc:
                messagebox.showerror("Registration failed", str(exc))

        row = ttk.Frame(card, style="Panel.TFrame")
        row.pack(anchor="e", pady=(4, 0))
        ttk.Button(row, text="Create account", command=register).pack(side="left", padx=(0, 10))
        ttk.Button(row, text="Sign in", style="Accent.TButton", command=login).pack(side="left")

    def show_search(self):
        self._clear()
        self._page_title("Find a movie", f"Signed in as {self.user['username']}")
        search_row = ttk.Frame(self.content)
        search_row.pack(fill="x")
        query = tk.StringVar()
        ttk.Entry(search_row, textvariable=query).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(search_row, text="Search", style="Accent.TButton", command=lambda: run_search()).pack(side="left")

        result = ttk.Frame(self.content, style="Panel.TFrame", padding=22)
        result.pack(fill="both", expand=True, pady=24)
        title = ttk.Label(result, text="Search for a title to begin.", style="Card.TLabel", font=("Segoe UI Semibold", 18))
        details = ttk.Label(result, text="", style="Card.TLabel", wraplength=650, justify="left")
        title.pack(anchor="w")
        details.pack(anchor="w", pady=(10, 20))

        actions = ttk.Frame(result, style="Panel.TFrame")
        actions.pack(anchor="w")
        ttk.Button(actions, text="Add favorite", command=lambda: self._save_current(add_favorite, "favorites")).pack(side="left", padx=(0, 10))
        ttk.Button(actions, text="Mark watched", command=lambda: self._save_current(mark_watched, "watch history")).pack(side="left")

        def run_search():
            if not query.get().strip():
                return
            movie = search_movie(query.get().strip())
            if movie.get("Response") != "True":
                messagebox.showinfo("No match", "I could not find that title.")
                return
            self.current_movie = movie
            # A single useful block beats scattering tiny labels all over the page.
            title.config(text=f"{movie.get('Title')} ({movie.get('Year')})")
            details.config(text=f"Genre: {movie.get('Genre', 'N/A')}\nRating: {movie.get('imdbRating', 'N/A')}\nDirector: {movie.get('Director', 'N/A')}\n\n{movie.get('Plot', 'No plot summary available.')}")

    def _save_current(self, saver, label):
        if not self.current_movie:
            messagebox.showinfo("Nothing selected", "Search for a movie first.")
            return
        saved = saver(self.user["id"], self.current_movie)
        messagebox.showinfo("Saved" if saved else "Already saved", f"Updated your {label}.")

    def show_library(self):
        self._clear()
        self._page_title("Your library", "Favorites and watch history are kept in the local database.")
        tabs = ttk.Notebook(self.content)
        tabs.pack(fill="both", expand=True)
        self._movie_table(tabs, "Favorites", list_favorites(self.user["id"]), "created_at")
        self._movie_table(tabs, "Watched", list_watch_history(self.user["id"]), "watched_date")

    def _movie_table(self, tabs, name, rows, date_key):
        frame = ttk.Frame(tabs, padding=12)
        tabs.add(frame, text=name)
        columns = ("title", "year", "genre", "rating", "date")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col, width in (("title", 220), ("year", 70), ("genre", 220), ("rating", 80), ("date", 140)):
            tree.heading(col, text=col.title())
            tree.column(col, width=width, anchor="w")
        tree.pack(fill="both", expand=True)

        # The database already knows the shape; the GUI only formats it for quick scanning.
        for row in rows:
            tree.insert("", "end", values=(row["movie_title"], row["year"], row["genre"], row["rating"], row.get(date_key, "")))


if __name__ == "__main__":
    CineTrackApp().mainloop()
