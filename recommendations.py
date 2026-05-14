def recommend_movies(movies):

    if len(movies) == 0:
        return "Save favorites or mark watched movies to unlock recommendations."

    genres = []

    for movie in movies:

        movie_genres = movie.get("Genre") or movie.get("genre", "")
        movie_genres = movie_genres.split(",")

        for genre in movie_genres:
            genre = genre.strip()
            if genre and genre != "N/A":
                genres.append(genre)

    if not genres:
        return "Your saved movies do not have enough genre data yet."

    genre_count = {}

    for genre in genres:

        if genre in genre_count:
            genre_count[genre] += 1

        else:
            genre_count[genre] = 1

    favorite_genre = max(genre_count, key=genre_count.get)

    return f"You seem to enjoy {favorite_genre} movies. Try searching for more in that mood."
