import sqlite3
from database_operations import *

database_path = os.path.join(os.path.dirname(__file__), "sem_diff_predi.db")

conn = sqlite3.connect(database_path)
cur = conn.cursor()

prereqs = cur.execute("SELECT * FROM course_prerequisite WHERE course_id = 5").fetchall()
print(prereqs)