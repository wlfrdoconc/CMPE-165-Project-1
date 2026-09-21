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

    connection.commit()
    connection.close()

    course_id = cursor.lastrowid

    return course_id

# Grabs the course_id based on a course_code. Used as a helper function in completed_course()
def get_course_id_by_code(course_code: str) -> int:
    connection = sqlite3.connect("sem_diff_predi.db")
    cursor = connection.cursor()

    res = cursor.execute("""
        SELECT course_id FROM course
        WHERE course_code = ?
    """, (course_code, )).fetchone()

    connection.close()
        
    if res is None:
        print('course_id does not exist.')
        return None

    return res[0]

# Adds a completed course to the database.
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
    """, (student_id, course_id, grade))

    connection.commit()
    connection.close()

    return True 

# Returns a set of classes that a student has already completed.
def get_completed_course_ids(student_id: int) -> set:
    connection = sqlite3.connect("sem_diff_predi.db")
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
    connection = sqlite3.connect("sem_diff_predi.db")
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
def available_classes(student_id: int):
    connection = sqlite3.connect("sem_diff_predi.db")
    cursor = connection.cursor()

    all_courses = cursor.execute("SELECT course_id FROM course").fetchall()
    connection.close()

    completed_courses = get_completed_course_ids(student_id)
    available = []

    for course in all_courses:
        if course[0] not in completed_courses and not check_prerequisites(course[0], student_id):
            available.append(course[0])

    return available