import sqlite3
from database_operations import *

conn = sqlite3.connect('sem_diff_predi.db')
cur = conn.cursor()

test = get_completed_course_ids(1)
print(f'Completed_courses: {test}')

test2 = check_prerequisites(1, 1)
print(f'prerequisites met status: {test2}')
test3 = available_classes(1)
print(f'Avaiable classes: {test3}')