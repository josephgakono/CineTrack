TITLE_STOP_WORDS = {"a", "an", "and", "of", "the"}


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


def _split_values(value):
    return [item.strip() for item in value.split(",") if item.strip() and item.strip() != "N/A"]


def _known_titles(movies):
    return {
        (movie.get("Title") or movie.get("movie_title") or "").strip().lower()
        for movie in movies
        if movie.get("Title") or movie.get("movie_title")
    }


def _title_queries(title):
    words = [
        word.strip(":,.-").lower()
        for word in title.split()
        if len(word.strip(":,.-")) > 3 and word.strip(":,.-").lower() not in TITLE_STOP_WORDS
    ]
    return [
        {"query": word, "kind": "title", "value": word, "reason": f"has a related title match for {word}"}
        for word in words[:2]
    ]


def _candidate_queries(seed_movie):
    genres = _split_values(seed_movie.get("Genre", ""))
    actors = _split_values(seed_movie.get("Actors", ""))
    director = seed_movie.get("Director", "").strip()

    queries = _title_queries(seed_movie.get("Title", ""))
    if genres:
        queries.append({"query": genres[0], "kind": "genre", "value": genres[0], "reason": f"shares the {genres[0]} genre"})
    if director and director != "N/A":
        queries.append({"query": director, "kind": "director", "value": director, "reason": f"also directed by {director}"})
    if actors:
        queries.append({"query": actors[0], "kind": "actor", "value": actors[0], "reason": f"features {actors[0]}"})

    return queries

