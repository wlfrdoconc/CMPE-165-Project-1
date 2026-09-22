CREATE TABLE IF NOT EXISTS student (
    student_id INTEGER PRIMARY KEY,
    major TEXT NOT NULL,
    student_year INTEGER,
    student_type TEXT NOT NULL,
    learning_style TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS course (
    course_id INTEGER PRIMARY KEY,
    course_code TEXT UNIQUE,
    title TEXT UNIQUE,
    course_description TEXT NOT NULL,
    units INTEGER NOT NULL,
    course_level TEXT NOT NULL,
    subject_area TEXT NOT NULL,
    course_type TEXT NOT NULL, 
    complexity_score INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS completed_course (
    student_id INTEGER,
    course_id INTEGER,
    grade CHAR,
    FOREIGN KEY(student_id) REFERENCES student(student_id),
    FOREIGN KEY(course_id) REFERENCES course(course_id),
    PRIMARY KEY(student_id, course_id)
);

CREATE TABLE IF NOT EXISTS course_prerequisite (
    course_id INTEGER,
    prerequisite_course_id INTEGER,
    FOREIGN KEY(course_id) REFERENCES course(course_id),
    FOREIGN KEY(prerequisite_course_id) REFERENCES course(course_id),
    PRIMARY KEY(course_id, prerequisite_course_id)
);

CREATE TABLE IF NOT EXISTS semester_plan (
    plan_id INTEGER PRIMARY KEY,
    student_id INTEGER,
    semester TEXT NOT NULL,
    semester_year INTEGER NOT NULL,
    difficulty_score INTEGER NOT NULL,
    workload_hours INTEGER NOT NULL,
    balance_rating INTEGER NOT NULL,
    warning_message TEXT NOT NULL,
    FOREIGN KEY(student_id) REFERENCES student(student_id)
);

CREATE TABLE IF NOT EXISTS plan_course (
    plan_id INTEGER,
    course_id INTEGER,
    prior_experience TEXT NOT NULL,
    difficulty_score INTEGER NOT NULL,
    estimated_hours INTEGER NOT NULL,
    FOREIGN KEY(plan_id) REFERENCES semester_plan(plan_id),
    FOREIGN KEY(course_id) REFERENCES course(course_id),
    PRIMARY KEY(plan_id, course_id)
);