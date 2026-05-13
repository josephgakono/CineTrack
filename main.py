from api import search_movie
from recommendations import recommend_movies
from favorites import add_to_favorites, view_favorites, favorites

movie_name = input("Enter movie name: ")

movie = search_movie(movie_name)
 

if movie["Response"] == "True":

    print("\nMovie Found")
    print(movie["Title"])
    print(movie["Genre"])

    add = input("\nAdd to favorites? (yes/no): ").lower()

    if add == "yes":
     add_to_favorites(movie)

     recommendation = recommend_movies(favorites)

     print("\nRecommendation:")
     print(recommendation)
    
    view = input("\nView favorite movies? (yes/no): ").lower()

    if view == "yes":
     view_favorites()

else:
    print("Movie not found.")
