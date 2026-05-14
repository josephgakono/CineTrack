import sqlite3

# Connect to database
conn = sqlite3.connect("CInetrack_Database.db")

# Create cursor
cursor = conn.cursor()

print("Database connected successfully.")