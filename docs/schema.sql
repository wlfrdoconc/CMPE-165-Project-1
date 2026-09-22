-- Local MVP persistence schema. See INTEGRATION.md for prerequisite expressions.

PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS course (
 course_id TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, catalog_year TEXT NOT NULL,
 title TEXT NOT NULL, units_min REAL NOT NULL, units_max REAL NOT NULL, record_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS course_ge (
 course_id TEXT NOT NULL REFERENCES course(course_id), area TEXT NOT NULL,
 PRIMARY KEY(course_id, area)
);
CREATE TABLE IF NOT EXISTS student (
 student_id TEXT PRIMARY KEY, profile_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS completed_course (
 student_id TEXT NOT NULL REFERENCES student(student_id), course_code TEXT NOT NULL, grade TEXT NOT NULL,
 PRIMARY KEY(student_id,course_code)
);
CREATE TABLE IF NOT EXISTS semester_plan (
 plan_id TEXT PRIMARY KEY, student_id TEXT NOT NULL REFERENCES student(student_id),
 name TEXT NOT NULL, created_at TEXT NOT NULL, payload_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS plan_course (
 plan_id TEXT NOT NULL REFERENCES semester_plan(plan_id), course_id TEXT NOT NULL REFERENCES course(course_id),
 prior_experience INTEGER NOT NULL, units REAL NOT NULL, difficulty_score REAL NOT NULL, estimated_hours REAL NOT NULL,
 PRIMARY KEY(plan_id,course_id)
);
