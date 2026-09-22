import math
import os
import sqlite3
import statistics

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

# Allow the student to create a semester plan. difficulty/workload/balance/warning start
# as placeholders and are filled in later by finalize_semester_plan().
def create_semester_plan(student_id: int, semester: str, semester_year: int) -> int:
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO semester_plan (student_id, semester, semester_year, difficulty_score, workload_hours, balance_rating, warning_message)
        VALUES (?, ?, ?, 0, 0, 0, '')
    """, (student_id, semester, semester_year))

    plan_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return plan_id

# Allow the student to add courses to an existing semester plan. Each plan_course row's
# difficulty_score/estimated_hours are copied from the course's own complexity_score/units
# (same 2.5 hrs/unit rate as calculate_workload_hours) since they describe that one course.
def add_course_to_plan(plan_id: int, course_id: int, prior_experience: str) -> bool:
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    plan_exists = cursor.execute("""
        SELECT plan_id FROM semester_plan
        WHERE plan_id = ?
    """, (plan_id, )).fetchone()

    if plan_exists is None:
        connection.close()
        return False

    course = cursor.execute("""
        SELECT complexity_score, units FROM course
        WHERE course_id = ?
    """, (course_id, )).fetchone()

    if course is None:
        connection.close()
        return False

    complexity_score, units = course
    estimated_hours = math.ceil(units * 2.5)

    cursor.execute("""
        INSERT INTO plan_course (plan_id, course_id, prior_experience, difficulty_score, estimated_hours)
        VALUES (?, ?, ?, ?, ?)
    """, (plan_id, course_id, prior_experience, complexity_score, estimated_hours))

    connection.commit()
    connection.close()

    return True

# Returns the set of course_ids currently in a semester plan.
def get_plan_course_ids(plan_id: int) -> set:
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    plan_course_ids = cursor.execute("""
        SELECT course_id FROM plan_course
        WHERE plan_id = ?
    """, (plan_id, )).fetchall()

    connection.close()

    result = set()

    for course_id in plan_course_ids:
        result.add(course_id[0])

    return result

# Estimated weekly workload for a plan: 2.5 hours per unit, rounded up.
def calculate_workload_hours(plan_id: int) -> int:
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    total_units = cursor.execute("""
        SELECT SUM(course.units) FROM plan_course
        JOIN course ON plan_course.course_id = course.course_id
        WHERE plan_course.plan_id = ?
    """, (plan_id, )).fetchone()[0]

    connection.close()

    if total_units is None:
        total_units = 0

    return math.ceil(total_units * 2.5)

# Overall difficulty of a plan: sum of complexity_score across its courses.
def calculate_difficulty_score(plan_id: int) -> int:
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    total_complexity = cursor.execute("""
        SELECT SUM(course.complexity_score) FROM plan_course
        JOIN course ON plan_course.course_id = course.course_id
        WHERE plan_course.plan_id = ?
    """, (plan_id, )).fetchone()[0]

    connection.close()

    if total_complexity is None:
        return 0

    return int(total_complexity)

# Rates how consistent the plan's course difficulty is (1-5). Complexity scores are on a
# 1-10 scale, so a low spread (courses of similar difficulty) rates high, and a wide spread
# (e.g. very easy courses mixed with very hard ones) rates low.
def calculate_balance_rating(plan_id: int) -> int:
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    rows = cursor.execute("""
        SELECT course.complexity_score FROM plan_course
        JOIN course ON plan_course.course_id = course.course_id
        WHERE plan_course.plan_id = ?
    """, (plan_id, )).fetchall()

    connection.close()

    scores = [row[0] for row in rows]

    if not scores:
        return 5

    spread = statistics.pstdev(scores)

    if spread == 0:
        return 5
    elif spread <= 1.5:
        return 4
    elif spread <= 3.0:
        return 3
    elif spread <= 4.5:
        return 2
    else:
        return 1

# Flags a heavy semester: 40+ estimated hours per week.
def generate_warning_message(workload_hours: int) -> str:
    if workload_hours >= 40:
        return f"Warning: this semester has a heavy estimated workload of {workload_hours} hours per week."

    return ""

# Writes computed values back into an existing semester_plan row.
def update_semester_plan(plan_id: int, difficulty_score: int, workload_hours: int, balance_rating: int, warning_message: str) -> bool:
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE semester_plan
        SET difficulty_score = ?, workload_hours = ?, balance_rating = ?, warning_message = ?
        WHERE plan_id = ?
    """, (difficulty_score, workload_hours, balance_rating, warning_message, plan_id))

    updated = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return updated

# Computes difficulty_score, workload_hours, balance_rating and warning_message for a plan
# and writes them back to its semester_plan row.
def finalize_semester_plan(plan_id: int) -> bool:
    difficulty_score = calculate_difficulty_score(plan_id)
    workload_hours = calculate_workload_hours(plan_id)
    balance_rating = calculate_balance_rating(plan_id)
    warning_message = generate_warning_message(workload_hours)

    return update_semester_plan(plan_id, difficulty_score, workload_hours, balance_rating, warning_message)