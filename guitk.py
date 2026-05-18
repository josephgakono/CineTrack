import tkinter as tk
from io import BytesIO
from tkinter import messagebox, ttk

import requests
from PIL import Image, ImageTk

from api import search_movie, search_movies
from database import (
    add_favorite,
    authenticate_user,
    delete_watch_entry,
    init_database,
    list_favorites,
    list_watch_history,
    mark_watched,
    recommendation_movies,
    remove_favorite,
    register_user,
)
from recommendations import recommend_movies, recommend_titles_from_movie


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
        self.poster_cache = {}
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
        for text, command in (
            ("Search", self.show_search),
            ("Library", self.show_library),
            ("Recommendations", self.show_recommendations),
            ("Sign out", self.show_login),
        ):
            tk.Button(self.nav, text=text, command=command, bg=COLORS["panel"], fg=COLORS["text"], relief="flat", anchor="w", padx=14, pady=10).pack(fill="x", pady=3)

    def _clear(self):
        for child in self.content.winfo_children():
            child.destroy()

    def _page_title(self, title, subtitle):
        ttk.Label(self.content, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.content, text=subtitle, style="Muted.TLabel").pack(anchor="w", pady=(2, 22))

    def _poster_image(self, poster_url, size=(86, 128)):
        if not poster_url or poster_url == "N/A":
            return None

        cache_key = (poster_url, size)
        if cache_key in self.poster_cache:
            return self.poster_cache[cache_key]

        try:
            response = requests.get(poster_url, timeout=8)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            image.thumbnail(size)
            photo = ImageTk.PhotoImage(image)
        except (requests.RequestException, OSError, tk.TclError):
            return None

        self.poster_cache[cache_key] = photo
        return photo

    def _poster_label(self, parent, poster_url, size=(86, 128)):
        photo = self._poster_image(poster_url, size)
        if photo:
            label = ttk.Label(parent, image=photo, style="Card.TLabel")
            label.image = photo
            return label

        return ttk.Label(parent, text="Poster\nunavailable", style="Card.TLabel", width=14, anchor="center", justify="center")

    def _movie_card(self, parent, title, subtitle, poster_url):
        item = ttk.Frame(parent, style="Panel.TFrame", padding=14)
        item.pack(fill="x", pady=5)
        self._poster_label(item, poster_url).pack(side="left", padx=(0, 14))
        copy = ttk.Frame(item, style="Panel.TFrame")
        copy.pack(side="left", fill="x", expand=True)
        ttk.Label(copy, text=title, style="Card.TLabel", font=("Segoe UI Semibold", 12)).pack(anchor="w")
        ttk.Label(copy, text=subtitle, style="Card.TLabel", wraplength=610).pack(anchor="w")
        return item

    def _scrollable_frame(self, parent):
        shell = ttk.Frame(parent)
        canvas = tk.Canvas(shell, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(shell, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def update_scroll_region(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def fit_inner_width(event):
            canvas.itemconfigure(window_id, width=event.width)

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        inner.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", fit_inner_width)
        canvas.bind("<Enter>", lambda _event: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda _event: canvas.unbind_all("<MouseWheel>"))

        return shell, inner

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
        poster_slot = ttk.Frame(result, style="Panel.TFrame")
        poster_slot.pack(side="left", anchor="n", padx=(0, 18))
        info = ttk.Frame(result, style="Panel.TFrame")
        info.pack(side="left", fill="both", expand=True)
        title = ttk.Label(info, text="Search for a title to begin.", style="Card.TLabel", font=("Segoe UI Semibold", 18))
        details = ttk.Label(info, text="", style="Card.TLabel", wraplength=650, justify="left")
        title.pack(anchor="w")
        details.pack(anchor="w", pady=(10, 20))

        actions = ttk.Frame(info, style="Panel.TFrame")
        actions.pack(anchor="w")
        favorite_button = ttk.Button(actions, text="Add favorite")
        watched_button = ttk.Button(actions, text="Mark watched")
        favorite_button.config(command=lambda: self._save_current(add_favorite, "favorites", favorite_button, "Added to favorites"))
        watched_button.config(command=lambda: self._save_current(mark_watched, "watch history", watched_button, "Marked as watched"))
        favorite_button.pack(side="left", padx=(0, 10))
        watched_button.pack(side="left")

        def run_search():
            if not query.get().strip():
                return
            movie = search_movie(query.get().strip())
            if movie.get("Response") != "True":
                messagebox.showinfo("No match", "I could not find that title.")
                return
            self.current_movie = movie
            # A single useful block beats scattering tiny labels all over the page.
            for child in poster_slot.winfo_children():
                child.destroy()
            self._poster_label(poster_slot, movie.get("Poster"), size=(118, 176)).pack(anchor="n")
            favorite_button.config(text="Add favorite")
            watched_button.config(text="Mark watched")
            title.config(text=f"{movie.get('Title')} ({movie.get('Year')})")
            details.config(text=f"Genre: {movie.get('Genre', 'N/A')}\nRating: {movie.get('imdbRating', 'N/A')}\nDirector: {movie.get('Director', 'N/A')}\n\n{movie.get('Plot', 'No plot summary available.')}")

    def _save_current(self, saver, label, button=None, saved_text=None):
        if not self.current_movie:
            messagebox.showinfo("Nothing selected", "Search for a movie first.")
            return
        saved = saver(self.user["id"], self.current_movie)
        if button and saved_text:
            button.config(text=saved_text if saved else "Already saved")
        messagebox.showinfo("Saved" if saved else "Already saved", f"Updated your {label}.")

    def show_library(self):
        self._clear()
        self._page_title("Your library", "Select a movie in Favorites or Watched, then choose Delete selected to remove it.")
        tabs = ttk.Notebook(self.content)
        tabs.pack(fill="both", expand=True)
        self._movie_table(tabs, "Favorites", list_favorites(self.user["id"]), "created_at", remove_favorite)
        self._movie_table(tabs, "Watched", list_watch_history(self.user["id"]), "watched_date", delete_watch_entry)

    def _movie_table(self, tabs, name, rows, date_key, delete_handler):
        frame = ttk.Frame(tabs, padding=12)
        tabs.add(frame, text=name)
        if not rows:
            ttk.Label(frame, text=f"No {name.lower()} movies yet.", style="Muted.TLabel").pack(anchor="w")
            return

        scroll_shell, list_frame = self._scrollable_frame(frame)
        scroll_shell.pack(fill="both", expand=True)

        for row in rows:
            title = f"{row['movie_title']} ({row.get('year', '')})"
            subtitle = f"{row.get('genre', 'Unknown')} | IMDb: {row.get('rating', 'N/A')} | {row.get(date_key, '')}"
            card = self._movie_card(list_frame, title, subtitle, row.get("poster"))
            ttk.Button(card, text="Delete", command=lambda movie=row, card=card: self._delete_library_movie(card, name, movie, delete_handler)).pack(side="right", anchor="n")

    def _delete_library_movie(self, card, list_name, movie, delete_handler):
        title = movie["movie_title"]
        if not messagebox.askyesno("Delete movie", f"Remove '{title}' from {list_name}?"):
            return

        delete_handler(self.user["id"], movie["id"])
        card.destroy()

    def show_recommendations(self):
        self._clear()
        movies = recommendation_movies(self.user["id"])
        self._page_title("Recommendations", "Enter a movie title to find genre-first related movie titles.")

        search_row = ttk.Frame(self.content)
        search_row.pack(fill="x", pady=(0, 18))
        seed_title = tk.StringVar()
        ttk.Entry(search_row, textvariable=seed_title).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(search_row, text="Recommend titles", style="Accent.TButton", command=lambda: run_title_recommendation()).pack(side="left")

        summary = ttk.Label(self.content, text=recommend_movies(movies), wraplength=700, font=("Segoe UI Semibold", 14))
        summary.pack(anchor="w", pady=(0, 18))

        results_shell, results = self._scrollable_frame(self.content)
        results_shell.pack(fill="both", expand=True)

        def show_recommendation_rows(recommendations, empty_message):
            for child in results.winfo_children():
                child.destroy()

            if not recommendations:
                ttk.Label(results, text=empty_message, style="Muted.TLabel").pack(anchor="w")
                return

            for movie in recommendations:
                self._movie_card(
                    results,
                    f"{movie['title']} ({movie.get('year', '')})",
                    f"{movie.get('genre', 'Unknown')} | IMDb: {movie.get('rating', 'N/A')} | {movie.get('reason', '')}",
                    movie.get("poster"),
                )

        def run_title_recommendation():
            title = seed_title.get().strip()
            if not title:
                messagebox.showinfo("Title needed", "Enter a movie title first.")
                return

            seed_movie = search_movie(title)
            if seed_movie.get("Response") != "True":
                messagebox.showinfo("No match", "I could not find that movie title.")
                return

            recommendations = recommend_titles_from_movie(seed_movie, movies, search_movies, search_movie)
            summary.config(text=f"Because you searched for {seed_movie.get('Title')}, here are genre-first related movie titles.")
            show_recommendation_rows(recommendations, "No title recommendations found. Try another movie title.")

        show_recommendation_rows([], "Enter a title above to generate movie recommendations.")


if __name__ == "__main__":
    CineTrackApp().mainloop()
