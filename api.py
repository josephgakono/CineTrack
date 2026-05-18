import requests

API_KEY = "aa15d8f5"


def search_movie(movie_name):
    response = requests.get(
        "http://www.omdbapi.com/",
        params={"t": movie_name, "apikey": API_KEY},
    )
    data = response.json()

    return data


def search_movies(query):
    response = requests.get(
        "http://www.omdbapi.com/",
        params={"s": query, "type": "movie", "apikey": API_KEY},
    )
    data = response.json()

    if data.get("Response") != "True":
        return []

    return data.get("Search", [])
