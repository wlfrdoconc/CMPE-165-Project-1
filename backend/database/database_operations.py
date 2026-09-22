import os
import sqlite3

database_path = os.path.join(os.path.dirname(__file__), "sem_diff_predi.db")

# Adds a student to the database. Parameters are not passed in directly to prevent SQL injections.
def add_student(major: str, student_year: int, student_type: str, learning_style: str) -> int:
    connection = sqlite3.connect(database_path)
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
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor() 

    if get_course_id_by_code(course_code) is not None:
        print('This course already exists.')
        return

    cursor.execute("""
        INSERT INTO course (course_code, title, course_description, units, course_level, subject_area, course_type, complexity_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (course_code, title, course_description, units, course_level, subject_area, course_type, complexity_score))

    connection.commit()
    connection.close()

    course_id = cursor.lastrowid

    return course_id

# Grabs the course_id based on a course_code. Used as a helper function in completed_course()
def get_course_id_by_code(course_code: str) -> int:
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    res = cursor.execute("""
        SELECT course_id FROM course
        WHERE course_code = ?
    """, (course_code, )).fetchone()

    connection.close()
        
    if res is None:
        return None

    return res[0]

# Adds a completed course to the database.
def add_completed_course(student_id: int, course_code: str, grade: str) -> bool:
    course_id = get_course_id_by_code(course_code)

    if course_id is None:
        print('course_id does not exist.')
        return None

    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO completed_course (student_id, course_id, grade)
        VALUES (?, ?, ?)
    """, (student_id, course_id, grade))

    connection.commit()
    connection.close()

    return True 

# Returns a set of classes that a student has already completed.
def get_completed_course_ids(student_id: int) -> set:
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    completed_courses_ids = cursor.execute("""
        SELECT course_id FROM completed_course
        WHERE student_id = ?
    """, (student_id, )).fetchall()

    connection.close()

    result = set()

    for course_id in completed_courses_ids:
        result.add(course_id[0])

    return result

# Compares the prerequisites of a course to the completed courses of a student.
def check_prerequisites(course_id: int, student_id: int) -> set:
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    course_prerequisites = cursor.execute("""
        SELECT prerequisite_course_id FROM course_prerequisite
        WHERE course_id = ?
    """, (course_id, )).fetchall()

    prereqs = set()

    for course_prerequisite in course_prerequisites:
        prereqs.add(course_prerequisite[0])

    connection.close()

    completed_courses = get_completed_course_ids(student_id)

    if prereqs.issubset(completed_courses):
        return set()
    else:
        missing_prerequisites = prereqs - completed_courses
        return missing_prerequisites

# Displays classes the student can take. 
def get_available_courses(student_id: int) -> list:
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    all_courses = cursor.execute("SELECT course_id FROM course").fetchall()
    connection.close()

    completed_courses = get_completed_course_ids(student_id)
    available = []

    for course in all_courses:
        if course[0] not in completed_courses and not check_prerequisites(course[0], student_id):
            available.append(course[0])

    return available

# Calculate 

# Allow the student to create a semester plan. 
def create_semester_plan(student_id: int, semester: str, semester_year: int) -> int:
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO semester_plan (student_id, semester, semester_year)
        VALUES (?, ?, ?)
    """, (student_id, semester, semester_year))

    plan_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return plan_id

# Allow the student to add courses to an existing semester plan
def add_course_to_plan(plan_id: int, course_id: int, prior_experience) -> bool:
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    check_plan_id_exists = cursor.execute("""
        SELECT plan_id FROM semester_plan
        WHERE plan_id = ?
    """ (plan_id, ))

    if not check_plan_id_exists:
        return False

    cursor.execute("""
        INSERT INTO plan_course (plan_id, course_id, prior_experience)
        VALUES (?, ?, ?)
    """, (plan_id, course_id, prior_experience))

    connection.commit()
    connection.close()

    return True