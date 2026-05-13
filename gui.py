import tkinter as tk
from tkinter import messagebox

from api import search_movie
from recommendations import recommend_movies


users = {"admin": "1234"}
user_favorites = {}
current_user = ""
current_movie = None


def clear_window():
    for widget in window.winfo_children():
        widget.destroy()


def register():
    username = username_entry.get()
    password = password_entry.get()

    if username == "" or password == "":
        messagebox.showwarning("Error", "Enter username and password")
    elif username in users:
        messagebox.showwarning("Error", "Username already exists")
    else:
        users[username] = password
        user_favorites[username] = []
        messagebox.showinfo("Success", "Account created")


def login():
    global current_user

    username = username_entry.get()
    password = password_entry.get()

    if username in users and users[username] == password:
        current_user = username
        user_favorites.setdefault(username, [])
        show_home_page()
    else:
        messagebox.showerror("Error", "Wrong username or password")


def logout():
    global current_user
    global current_movie

    current_user = ""
    current_movie = None
    show_login_page()


def show_login_page():
    global username_entry
    global password_entry

    clear_window()

    tk.Label(window, text="CineTrack Login", font=("Arial", 18, "bold")).pack(pady=20)

    tk.Label(window, text="Username").pack()
    username_entry = tk.Entry(window, width=30)
    username_entry.pack()

    tk.Label(window, text="Password").pack()
    password_entry = tk.Entry(window, width=30, show="*")
    password_entry.pack()

    tk.Button(window, text="Login", width=15, command=login).pack(pady=8)
    tk.Button(window, text="Register", width=15, command=register).pack()


def search():
    global current_movie

    title = movie_entry.get()

    if title == "":
        messagebox.showwarning("Error", "Enter a movie title")
        return

    try:
        movie = search_movie(title)
    except Exception:
        messagebox.showerror("Error", "Could not connect to the movie API")
        return

    if movie["Response"] == "True":
        current_movie = movie
        movie_details.config(
            text=f"Title: {movie['Title']}\n"
            f"Year: {movie['Year']}\n"
            f"Genre: {movie['Genre']}\n"
            f"IMDb Rating: {movie['imdbRating']}"
        )
    else:
        current_movie = None
        movie_details.config(text="Movie not found")


def add_favorite():
    if current_movie is None:
        messagebox.showwarning("Error", "Search for a movie first")
        return

    user_favorites[current_user].append(current_movie)
    favorites_list.insert(tk.END, current_movie["Title"])
    recommendation_label.config(text=recommend_movies(user_favorites[current_user]))


def show_home_page():
    global movie_entry
    global movie_details
    global favorites_list
    global recommendation_label

    clear_window()

    tk.Label(window, text=f"Welcome {current_user}", font=("Arial", 16, "bold")).pack(pady=10)

    movie_entry = tk.Entry(window, width=40)
    movie_entry.pack(pady=5)

    tk.Button(window, text="Search Movie", command=search).pack(pady=5)

    movie_details = tk.Label(window, text="", justify="left", wraplength=420)
    movie_details.pack(pady=10)

    tk.Button(window, text="Add to Favorites", command=add_favorite).pack(pady=5)

    tk.Label(window, text="Favorite Movies").pack(pady=(15, 0))
    favorites_list = tk.Listbox(window, width=45, height=6)
    favorites_list.pack()

    for movie in user_favorites[current_user]:
        favorites_list.insert(tk.END, movie["Title"])

    recommendation_label = tk.Label(window, text=recommend_movies(user_favorites[current_user]))
    recommendation_label.pack(pady=10)

    tk.Button(window, text="Logout", command=logout).pack()


window = tk.Tk()
window.title("Movie Recommendation System")
window.geometry("500x520")

show_login_page()
window.mainloop()
