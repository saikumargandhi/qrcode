import sqlite3
import hashlib

conn = sqlite3.connect('database.db')
print("Created database successfully")

conn.execute('INSERT INTO users (name, mail, gender, pwd, mobile, role, year, branch, resetpassword) VALUES ("admin","admin@gmail.com","male","'+hashlib.sha256('admin'.encode()).hexdigest()+'","9059162048","0","","","")')
print("Default Admin account created successfully")
conn.commit()
conn.close()
