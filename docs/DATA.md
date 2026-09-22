# Catalog snapshot and interpretation

Collected September 21, 2026 from SJSU's public 2026–2027 catalog:

- [GE requirements and complete course options](https://catalog.sjsu.edu/preview_program.php?catoid=23&poid=18673)
- [Software Engineering degree requirements](https://catalog.sjsu.edu/preview_program.php?catoid=23&poid=18924)
- [Suggested four-year roadmap](https://catalog.sjsu.edu/preview_program.php?catoid=23&poid=19349&returnto=8647)

There are 475 GE course/area listings representing 467 distinct catalog courses. Courses can appear in multiple areas, so summing listings does not count distinct courses. The combined dataset contains 492 unique courses and a full course-detail capture for every record.

`ge_index.json` retains the exact GE heading, catalog ID, and listing text. `course_details.json` retains GE and extra math course details; `roadmap_course_details.json` retains the 30 roadmap records. `program.json` and `ge.json` retain policy-page text. `scripts/build_dataset.py` reads these sources without network access. No student data, MySJSU login, or RateMyProfessor material was collected.

## Conditions retained

- `(L)` listings in 5A/5B additionally carry 5C laboratory membership.
- Intensive sequences, specified-major-only listings, and sequence requirements remain in `ge_memberships`. Membership is not unconditional individual eligibility or automatic degree credit.
- Variable units stay a range, not a guessed single value.
- US/American Institutions conditions and cross-listing information remain in original text. The MVP does not automatically audit US1/2/3 or cross-listed duplicate credit.
- The capstone's four-course combination and minimum grades are required for the stated engineering GE overlap.
- Six technical elective units require advisor consultation; the degree page does not supply an exhaustive approved technical-elective list, so none is invented.
- SWE degree grade minimums can be stricter than a later course's enrollment prerequisite.

## Updating

Collect a new catalog-year snapshot in a separate directory, preserving IDs, exact text, source URLs, and retrieval date. Review structural changes before normalizing. Do not silently combine old and new catalog years. The current app intentionally pins 2026–2027.

## Scoring and eligibility limitations

Description keywords are a rough workload proxy, equally applied to technical and nontechnical subjects; they do not measure actual conceptual difficulty. The model's ±20% range is illustrative. Validate and calibrate with consenting student feedback before making stronger claims.

Eligibility has manually modeled normal-path rules for selected SWE courses. Other courses with prerequisites require review except the exact standard upper-division GE prerequisite statement. Student-confirmed conditions are explicitly labeled and are not official verification. Instructor consent, placement, transfer articulation, repeat-credit restrictions, and course availability are not inferred.
