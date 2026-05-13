favorites = []

def add_to_favorites(movie):

    favorites.append(movie)

    print(f"\n{movie['Title']} added to favorites.")


def view_favorites():

    if len(favorites) == 0:
        print("\nNo favorite movies yet.")
        return

    print("\n===== Favorite Movies =====\n")

    for movie in favorites:

        print(f"Title: {movie['Title']}")
        print(f"Year: {movie['Year']}")
        print("-" * 30)