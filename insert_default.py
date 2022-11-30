import sqlite3
import hashlib

conn = sqlite3.connect('database.db')
print("Created database successfully")

conn.execute('INSERT INTO users (name, mail, gender, pwd, mobile, role, year, branch, resetpassword) VALUES ("admin","admin@gmail.com","male","'+hashlib.sha256('admin'.encode()).hexdigest()+'","9059162048","0","","","")')
print("Default Admin account created successfully")

conn.execute('INSERT INTO books (book_name, year) VALUES ("Database Mangement System","2012")')

conn.execute('INSERT INTO books (book_name, year) VALUES ("Machine Learning Basics","2018")')

conn.execute('INSERT INTO books (book_name, year) VALUES ("Flask - Python Architecture","2021")')

print("Default Books created successfully")

conn.commit()
conn.close()
