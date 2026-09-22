import sqlite3

connection = sqlite3.connect("sem_diff_predi.db")
cursor = connection.cursor()

with open("schema.sql", "r") as f:
    schema_sql = f.read()

cursor.executescript(schema_sql)

connection.commit()
connection.close()