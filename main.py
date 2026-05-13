from api import search_movie


movie_name = input("Enter movie name: ")

movie = search_movie(movie_name)
 
if movie["Response"] == "True":

    print("\nMovies Found:\n")

    for item in movie["Search"]:

        print(f"Title: {item['Title']}")
        print(f"Year: {item['Year']}")
        print(f"Type: {item['Type']}")
        print("-" * 30)

else:
    print("Movie not found.")
