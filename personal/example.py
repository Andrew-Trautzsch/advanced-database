import argparse
import sqlite3
from pprint import pprint

ap = argparse.ArgumentParser()
ap.add_argument("--db", default="pets.db")
args = ap.parse_args()

conn = sqlite3.connect(args.db)

conn.execute("DROP table IF EXISTS pet")

conn.execute(
    """
    CREATE TABLE pet
    (
        id integer primary key autoincrement,
        name varchar(50) NOT NULL,
        kind varchar(50) NOT NULL,
        age integer,
        food varchar(50)
    )
    """
)

print("Success!")

#list tables
cursor = conn.execute(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name ASC
    """
)

list_of_tables =[item[0] for item in cursor.fetchall()]
# print(f"the table: {list_of_tables}")

cursor = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
                      ("pet",))
row = cursor.fetchone()
# pprint(row[0] if row else "")

cursor = conn.execute("SELECT * FROM pet")
row = cursor.fetchall()
# pprint(row)


try:
    conn.execute(
        "DELETE FROM pet WHERE name = ?",("Pepper",),
    )
    conn.commit()
    conn.execute(
        "INSERT INTO pet (name, kind, age, food) values (?,?,?,?)",
        ("Pepper","Cat",3,"tuna"),
    )
    conn.commit()
    print("Insert Succeeded")
except sqlite3.Error as e:
    print("Caught SQLite Error:", e)

print("done.")