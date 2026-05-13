from api import search_movie
from recommendations import recommend_movies

favorites = []

movie_name = input("Enter movie name: ")

movie = search_movie(movie_name)
 

if movie["Response"] == "True":

    print("\nMovie Found")
    print(movie["Title"])
    print(movie["Genre"])

    favorites.append(movie)

    recommendation = recommend_movies(favorites)

    print("\nRecommendation:")
    print(recommendation)

else:
    print("Movie not found.")
