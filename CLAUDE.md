# Semester Difficulty Predictor

A student project that predicts how difficult an upcoming semester will be, based on the courses a student selects, their prerequisites, and their academic history.

## Tech Stack

- **Backend / Database:** Python, SQLite
- **Frontend:** Streamlit

## Team & Roles

- **Will** — PM / Backend, designed the ERD
- **Joseph** — Backend & Database (implements the ERD: schema + database operations)
- **Mel** — Frontend & Assignment Questions

## MVP Flow

1. User builds a profile using their year, learning style, and previously completed classes.
2. System outputs a list of classes the user is eligible to take (prerequisites met, not already completed).
3. User selects a combination of classes for their upcoming semester.
4. System tells the user how difficult that semester will be.

## Data Model

Six tables, matching the project ERD:

- **student** — `student_id` (PK), `major`, `student_year`, `student_type`, `learning_style`
- **course** — `course_id` (PK), `course_code`, `title`, `course_description`, `units`, `course_level`, `subject_area`, `course_type`, `complexity_score`
- **completed_course** — junction table; composite PK `(student_id, course_id)`, plus `grade`. FKs to `student` and `course`.
- **course_prerequisite** — junction table; composite PK `(course_id, prerequisite_course_id)`. Both columns are FKs to `course` — `course_id` is the course being taken, `prerequisite_course_id` is the course required beforehand.
- **semester_plan** — `plan_id` (PK), `student_id` (FK), `semester`, `semester_year`, `difficulty_score`, `workload_hours`, `balance_rating`, `warning_message`
- **plan_course** — junction table; composite PK `(plan_id, course_id)`, plus `prior_experience`, `difficulty_score`, `estimated_hours`. FKs to `semester_plan` and `course`.

Table creation order (respecting FK dependencies): `student`, `course` → `completed_course`, `course_prerequisite`, `semester_plan` → `plan_course`.

## File Layout

```
backend/
    database/
        schema.sql              # all CREATE TABLE statements, in dependency order
        create_tables.py        # reads schema.sql and executes it against the .db file
        database_operations.py  # Python functions wrapping all DB reads/writes
        sem_diff_predi.db       # the SQLite database file
```

SQL lives in `schema.sql`, separate from the Python that executes it, so the schema can be scanned on its own against the ERD.

## Database Operations (`database_operations.py`)

Plain functions, no class — each operation is self-contained (connect, do one thing, close), so there's no shared state to justify a class wrapper.

**Completed:**
- `add_student(major, student_year, student_type, learning_style) -> int` — inserts a student, returns the new `student_id`.
- `add_course(course_code, title, course_description, units, course_level, subject_area, course_type, complexity_score)` — inserts a course; checks `course_code` doesn't already exist first.
- `get_course_id_by_code(course_code) -> int | None` — looks up a course's internal ID from its human-readable code. Returns `None` if not found (expected/normal case, not an exception).
- `add_completed_course(student_id, course_code, grade) -> bool` — resolves `course_code` via `get_course_id_by_code`, then inserts into `completed_course`.
- `get_completed_course_ids(student_id) -> list[int]` — all course IDs a student has completed.
- `check_prerequisites(course_id, student_id) -> list[int]` — always returns a list; empty means all prerequisites are met, non-empty lists the missing prerequisite course IDs.
- `get_available_courses(student_id) -> list[int]` — courses not yet completed AND with no missing prerequisites, using the two functions above.
- `create_semester_plan(student_id, semester, semester_year) -> int` — inserts a `semester_plan` row (difficulty/workload/balance/warning fields left for later), returns the new `plan_id`.
- `add_course_to_plan(plan_id, course_id, prior_experience) -> bool` — validates `plan_id` exists, then inserts into `plan_course`.

**In progress / not yet started (MVP step 4 — "tell the user how difficult the semester will be"):**
- Helper to get all `course_id`s for a given `plan_id` from `plan_course` (same shape as `get_completed_course_ids`, querying `plan_course` instead).
- `calculate_workload_hours(plan_id) -> int` — **designed, not yet implemented.** See formula below.
- Calculation for `difficulty_score` — combining each selected course's `complexity_score`. Formula not yet finalized by the team; starting point is aggregating `complexity_score` across the plan's courses. Still deciding sum vs. average.
- Calculation for `balance_rating`.
- `warning_message` generation logic (not yet designed).
- Function(s) to write these computed values back into the existing `semester_plan` row — an `UPDATE`, not an `INSERT`, since the row already exists from `create_semester_plan`.

### `calculate_workload_hours(plan_id)` — design

Rule of thumb: expect 2–3 hours of study per unit per week. Using the unbiased midpoint (2.5) rather than the high end, so the estimate reflects an honest expected workload rather than a deliberate overestimate.

```
total_units = sum(units for each course in plan_course where plan_id = plan_id)
workload_hours = ceil(total_units * 2.5)
```

- `total_units` comes from summing `course.units` across every course in the given plan (join `plan_course` → `course` on `course_id`).
- Round up (`math.ceil`, not `round()`) on the final result only — not on the per-unit rate — so the estimate stays honest and only nudges conservative at the very last step.
- `workload_hours` is `INTEGER` in the schema, so the result must be an int after rounding.

## Key SQLite Practices Used

- `sqlite3.connect(database_path)` with a single shared `database_path` constant.
- Parameterized queries (`?` placeholders + a tuple of values) everywhere user-influenced data touches SQL — never string-splicing values into SQL text (SQL injection risk).
- `cursor.lastrowid` to retrieve auto-generated primary keys (`student_id`, `plan_id`) right after an INSERT.
- `connection.commit()` required after every write, before `connection.close()` — a missing commit silently discards the change even though no exception is raised.
- Every `CREATE TABLE` uses `IF NOT EXISTS` so `schema.sql` can be re-run safely during development.
- Functions that "look something up and might not find it" (e.g. `get_course_id_by_code`) return `None` rather than raising an exception — not finding a match is normal/expected user behavior, not a bug.
- Functions that report success/failure for an INSERT return a consistent type across all code paths (always `bool`, or always a `list`) rather than mixing return types depending on the outcome.

## Git

Feature branches follow the pattern `feature/<short-description>` (e.g. `feature/student-course-tables`), one per unit of work.
