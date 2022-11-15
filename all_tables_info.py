import sqlite3

with sqlite3.connect("database.db") as con:
    cur = con.cursor()

    cur.execute("select * from users")
    rows = cur.fetchall()
    print("\n  ----------------")
    print("  Users Table")
    print("  ----------------\n")
    for row in rows:
        for col in row:
            print(col, end=" | ")
        print()
        
print()
con.close()