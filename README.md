# Movie Tracker System(CineTrack)

## Project Overview
The Movie Tracker System is a Python-based desktop application developed using Tkinter. It allows users to search for movies, save favorites, track watched movies, and view basic recommendations based on their preferences.

The system also stores user data locally using a database and retrieves movie information from an external movie API.

---

## Features

### 1. User Authentication
- Users can register and log in
- User credentials are stored in a local database

### 2. Movie Search
- Users can search for movies by title
- Displays movie details such as title, year, genre, rating, and poster

### 3. Favorites List
- Users can add movies to a favorites list
- Users can view and remove movies from favorites

### 4. Watch History
- Users can mark movies as watched
- Watched movies are stored and displayed in history

### 5. Recommendations
- The system recommends movies based on genres of previously liked or watched movies

---

## Technologies Used
- Python
- Tkinter (GUI)
- SQLite (Database)
- OMDb API (Movie data source)
- JSON (Data handling)

---

## System Requirements
- Python 3.x
- Internet connection (for API requests)
- Required library:
  - requests
  - Pillow

Install required library using:

 ```bash
 pip install requests Pillow
 ```


## How to Run the Project
1. Download or clone the project files
2. Open the project folder
3. Run the main file:

```bash
python3 main.py
```


---

## How to Use
1. Launch the application
2. Register or log in
3. Search for movies
4. Add movies to favorites or watch history
5. View recommendations based on your activity


## Project Structure
- main.py - Main application file
- gui.py - Handles Tkinter interface
- database.py - Handles SQLite database operations
- api.py - Handles movie API requests
- recommendations.py - Handles recommendation logic

## Future Improvements
- Improved recommendation system
- Better UI design
- Advanced filtering and search options
- Movie sorting in favorites and history
- Enhanced movie details display

## Screenshots
![Login page](/images/screenshot%20(2).png)
![Search page](/images/screenshot%20(3).png)
![Library page](/images/screenshot%20(1).png)