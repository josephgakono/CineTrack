def recommend_movies(favorites):

    if len(favorites) == 0:
        return "No favorite movies available."

    genres = []

    for movie in favorites:

        movie_genres = movie["Genre"].split(",")

        for genre in movie_genres:
            genres.append(genre.strip())

    genre_count = {}

    for genre in genres:

        if genre in genre_count:
            genre_count[genre] += 1

        else:
            genre_count[genre] = 1

    favorite_genre = max(genre_count, key=genre_count.get)

    return f"You seem to enjoy {favorite_genre} movies."