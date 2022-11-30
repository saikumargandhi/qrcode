import sqlite3
import hashlib

conn = sqlite3.connect('database.db')
print("Created database successfully")

conn.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, mail TEXT, gender TEXT, pwd TEXT, mobile TEXT, role INTEGER, year TEXT, branch TEXT, resetpassword TEXT)')
print("Users table created successfully")

conn.execute(
    'CREATE TABLE books (book_id INTEGER PRIMARY KEY AUTOINCREMENT, book_name TEXT,year TEXT)')
print("Users table created successfully")

conn.execute('CREATE TABLE assign_books (assign_id INTEGER PRIMARY KEY AUTOINCREMENT, stu_id INTEGER, assign_book_id INTEGER, assign_date TEXT)')
print("Assign Books table created successfully")

conn.close()
