import sqlite3
from pprint import pprint

connection = None

def initalize(database_file):
    global connection
    connection = sqlite3.connect(database_file, check_same_thread=False)
    
    connection.row_factory = sqlite3.Row
    
    print("Connection Established")
initalize("pets.db")
cursor = connection.execute("select * from pet")
rows = (dict[row] for row in cursor.fetchall())
pprint(rows)