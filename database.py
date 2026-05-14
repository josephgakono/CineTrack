import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path


DB_PATH = Path(__file__).with_name("CInetrack_Database.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _column_names(conn, table_name):
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table_name})")}


def _add_column(conn, table_name, column_sql):
    column_name = column_sql.split()[0]
    if column_name not in _column_names(conn, table_name):
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_sql}")


def init_database():
    with closing(get_connection()) as conn:
        # The app has had a few lives already, so these statements are deliberately
        # kind to older classroom databases instead of assuming a fresh install.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_title TEXT NOT NULL,
                genre TEXT,
                year TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS watch_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_title TEXT NOT NULL,
                watched_date TEXT
            )
            """
        )

        for table_name in ("favorites", "watch_history"):
            _add_column(conn, table_name, "user_id INTEGER")
            _add_column(conn, table_name, "imdb_id TEXT")
            _add_column(conn, table_name, "poster TEXT")
            _add_column(conn, table_name, "rating TEXT")

        _add_column(conn, "favorites", "created_at TEXT")
        _add_column(conn, "watch_history", "genre TEXT")
        _add_column(conn, "watch_history", "year TEXT")

        conn.commit()


def register_user(username, password):
    init_database()
    username = username.strip()
    if not username or not password:
        raise ValueError("Username and password are required.")

    with closing(get_connection()) as conn:
        try:
            cursor = conn.execute(
                "INSERT INTO Users (username, password) VALUES (?, ?)",
                (username, password),
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as exc:
            raise ValueError("That username is already taken.") from exc


def authenticate_user(username, password):
    init_database()
    with closing(get_connection()) as conn:
        row = conn.execute(
            "SELECT id, username FROM Users WHERE username = ? AND password = ?",
            (username.strip(), password),
        ).fetchone()
        return dict(row) if row else None


def _movie_values(movie, user_id):
    return {
        "user_id": user_id,
        "title": movie.get("Title", "Untitled"),
        "genre": movie.get("Genre", "Unknown"),
        "year": movie.get("Year", ""),
        "imdb_id": movie.get("imdbID", ""),
        "poster": movie.get("Poster", ""),
        "rating": movie.get("imdbRating", ""),
    }


def add_favorite(user_id, movie):
    init_database()
    values = _movie_values(movie, user_id)
    with closing(get_connection()) as conn:
        existing = conn.execute(
            """
            SELECT id FROM favorites
            WHERE user_id = ? AND (imdb_id = ? OR movie_title = ?)
            """,
            (user_id, values["imdb_id"], values["title"]),
        ).fetchone()
        if existing:
            return False

        conn.execute(
            """
            INSERT INTO favorites
                (user_id, movie_title, genre, year, imdb_id, poster, rating, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                values["title"],
                values["genre"],
                values["year"],
                values["imdb_id"],
                values["poster"],
                values["rating"],
                datetime.now().strftime("%Y-%m-%d %H:%M"),
            ),
        )
        conn.commit()
        return True


def remove_favorite(user_id, favorite_id):
    with closing(get_connection()) as conn:
        conn.execute(
            "DELETE FROM favorites WHERE id = ? AND user_id = ?",
            (favorite_id, user_id),
        )
        conn.commit()


def list_favorites(user_id):
    init_database()
    with closing(get_connection()) as conn:
        rows = conn.execute(
            """
            SELECT id, movie_title, genre, year, imdb_id, poster, rating, created_at
            FROM favorites
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def mark_watched(user_id, movie):
    init_database()
    values = _movie_values(movie, user_id)
    with closing(get_connection()) as conn:
        existing = conn.execute(
            """
            SELECT id FROM watch_history
            WHERE user_id = ? AND (imdb_id = ? OR movie_title = ?)
            """,
            (user_id, values["imdb_id"], values["title"]),
        ).fetchone()
        if existing:
            return False

        conn.execute(
            """
            INSERT INTO watch_history
                (user_id, movie_title, genre, year, imdb_id, poster, rating, watched_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                values["title"],
                values["genre"],
                values["year"],
                values["imdb_id"],
                values["poster"],
                values["rating"],
                datetime.now().strftime("%Y-%m-%d %H:%M"),
            ),
        )
        conn.commit()
        return True


def list_watch_history(user_id):
    init_database()
    with closing(get_connection()) as conn:
        rows = conn.execute(
            """
            SELECT id, movie_title, genre, year, imdb_id, poster, rating, watched_date
            FROM watch_history
            WHERE user_id = ?
            ORDER BY watched_date DESC, id DESC
            """,
            (user_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def delete_watch_entry(user_id, history_id):
    with closing(get_connection()) as conn:
        conn.execute(
            "DELETE FROM watch_history WHERE id = ? AND user_id = ?",
            (history_id, user_id),
        )
        conn.commit()


def recommendation_movies(user_id):
    return list_favorites(user_id) + list_watch_history(user_id)
