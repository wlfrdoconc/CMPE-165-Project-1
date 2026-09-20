import sqlite3

# Adds a student to the database. Parameters are not passed in directly to prevent SQL injections.
def add_student(major: str, student_year: int, student_type: str, learning_style: str) -> int:
    connection = sqlite3.connect("sem_diff_predi.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO student (major, student_year, student_type, learning_style)
        VALUES (?, ?, ?, ?)
    """, (major, student_year, student_type, learning_style))

    student_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return student_id

# Adds a course to the database.
def add_course(course_code: str, title: str, course_description: str, units: int, course_level: str, subject_area: str, course_type: str, complexity_score: int) -> int:
    connection = sqlite3.connect("sem_diff_predi.db")
    cursor = connection.cursor() 

    if get_course_id_by_code(course_code) is not None:
        print('This course already exists.')
        return

    cursor.execute("""
        INSERT INTO course (course_code, title, course_description, units, course_level, subject_area, course_type, complexity_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (course_code, title, course_description, units, course_level, subject_area, course_type, complexity_score))

    course_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return course_id

# Grabs the course_id based on a course_code. Used as a helper function in completed_course()
def get_course_id_by_code(course_code: str) -> int:
    connection = sqlite3.connect("sem_diff_predi.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT course_id FROM course
        WHERE course_code = ?
    """, (course_code, ))

    res = cursor.fetchone()
        
    if res is None:
        print('course_id does not exist.')
        return None

    return res[0]

# 
def add_completed_course(student_id: int, course_code: str, grade: str) -> bool:
    course_id = get_course_id_by_code(course_code)

    if course_id is None:
        print('course_id does not exist.')
        return None

    connection = sqlite3.connect("sem_diff_predi.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO completed_course (student_id, course_id, grade)
        VALUES (?, ?, ?)
    """, (student_id, course_code, grade))

    connection.commit()
    connection.close()

    return True 

