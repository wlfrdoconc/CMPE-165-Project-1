# Integration with Joseph's backend

No changes to Joseph's backend or database have been made. This adapter is a working local reference to compare later.

## Stable identifiers

Use `(catalog_year, code)` for cross-referencing, e.g. `("2026-2027", "CS 146")`. `course_id` is `sjsu:23:198982`; `catalog_id` belongs to SJSU's catalog, not our database. Never assume Joseph's integer primary keys equal these identifiers. Cross-listed courses remain separate catalog records and must not automatically earn duplicate credit.

## Data contract

`courses.json` has `schema_version`, `catalog_year`, `retrieved_on`, and `courses`.

Each course includes:

| Field | Meaning |
|---|---|
| `course_id`, `code`, `catalog_id` | Stable source identity and readable code |
| `title`, `description`, `subject`, `level` | Catalog content; level derived from course number |
| `units_min`, `units_max` | Unit range; selection supplies actual units |
| `prerequisites_raw`, `corequisites_raw`, `notes` | Original requirements preserved without flattening |
| `ge_areas`, `ge_memberships` | Many-to-many areas plus exact listing conditions |
| `swe_role` | Roadmap option, GE option, or additional math option; not a degree-audit allocation |
| `source_url`, `source_text`, `catalog_year` | Provenance and reviewable original text |

`requirements.json` keeps degree requirement groups separate from course records. Difficulty is computed from user context; it is not an official static course attribute.

## ERD adjustments

The reference ERD is implemented as course, course_ge, student, completed_course, semester_plan, and plan_course. Complex prerequisites are represented in `eligibility.RULES` as nested `all` / `any` / `course` expressions with minimum grades, unit thresholds, and explicit confirmation flags. A simple `(course, prerequisite)` edge cannot express `(A OR B) AND C`, grade thresholds, placement, or consent. Keep the raw text and full expression when Joseph maps these to his schema.

Student profiles and saved result snapshots are stored as JSON in SQLite as well as plan-course rows. The profile snapshot on a plan preserves historical inputs even after the current profile changes. Completed courses use a course-code field so external prerequisites not included in our catalog can still be represented. Grades of CR/unknown remain unresolved until verified. Saved plans contain the scoring version and dataset hash.

## Functions to connect

```python
from predictor.eligibility import Student, check
from predictor.scoring import estimate_semester

student = Student(year=2, earned_units=32,
                  completed={"CS 46B": "B"}, java_46b=True)
status = check(course_record, student, planned=["CMPE 131"])
result = estimate_semester(course_records, student,
                           experiences={"CMPE 131": 1}, unit_choices={})
```

Replace `repository.initialize`, `load_courses`, `save_plan`, and `list_plans` with calls to Joseph's backend, leaving scoring and UI contracts intact. A saved-plan export contains `schema_version`, `catalog_year`, `dataset_sha256`, `student`, `result`, and per-course `eligibility`.

## Reconciliation checklist

1. Match course codes and catalog years, then compare units and requirement text.
2. Review OR/AND semantics, grade minimums, placement conditions, major restrictions, and corequisites together.
3. Keep missing information as unknown; do not turn missing prerequisite rows into automatic eligibility.
4. Decide whether Joseph's backend owns rules and scoring or calls these pure Python functions.
5. Establish migrations and authentication before any shared deployment. The current anonymous local session is for prototype demonstrations.
