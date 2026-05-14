from database import add_favorite, list_favorites


favorites = []
current_user_id = 1


def set_current_user(user_id):
    global current_user_id
    current_user_id = user_id


def add_to_favorites(movie, user_id=None):
    user_id = user_id or current_user_id
    saved = add_favorite(user_id, movie)
    title = movie.get("Title", "Movie")
    print(f"\n{title} {'added to' if saved else 'is already in'} favorites.")
    return saved


def view_favorites(user_id=None):
    user_id = user_id or current_user_id
    saved_movies = list_favorites(user_id)
    favorites[:] = saved_movies

    if not saved_movies:
        print("\nNo favorite movies yet.")
        return []

    print("\n===== Favorite Movies =====\n")
    for movie in saved_movies:
        print(f"Title: {movie['movie_title']}")
        print(f"Year: {movie.get('year', '')}")
        print("-" * 30)
    return saved_movies
