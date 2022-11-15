import sqlite3
import hashlib

conn = sqlite3.connect('database.db')
print("Created database successfully")

conn.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, mail TEXT, gender TEXT, pwd TEXT, mobile TEXT, role INTEGER, year TEXT, branch TEXT, resetpassword TEXT)')
print("Users table created successfully")
conn.close()
