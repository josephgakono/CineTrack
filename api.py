import requests

API_KEY = "http://www.omdbapi.com/?i=tt3896198&apikey=aa15d8f5"

def search_movie(movie_name):
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={API_KEY}"

    response = requests.get(url)
    data = response.json()

    return data