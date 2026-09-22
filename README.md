# Semester Compass

A semester difficulty predictor for SJSU Software Engineering students. Built with Python, Streamlit, and SQLite using the 2026–2027 catalog.

It helps students compare course combinations and plan a manageable workload before choosing their semester schedule.

## Team

- **Wilfredo Concepcion (Will)** — Project Manager / Full-Stack
- **Joseph Centeno** — Backend / Database
- **Melody Deng** — Independent Reports / Slides

## Requirements

Python 3.11+ (tested with 3.14). Streamlit is listed in `requirements.txt`; pytest is in `requirements-dev.txt`. SQLite is included with Python. The install commands below also install package dependencies.

## Run

Open a terminal in the project folder. On macOS/Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows PowerShell, use `python` instead of `python3` and activate with `.venv\Scripts\Activate.ps1`.

Open [localhost:8501](http://localhost:8501) and click **Load sample student** to try it.

The course dataset is included in `data/sjsu/2026-2027/`. No account or live scraping is needed to run the app.

## How to use

1. **Your background:** Enter your year and completed courses. Add grades and other details when needed.
2. **Pick courses:** Search SWE or GE options and add them to your plan.
3. **Review semester:** View estimated difficulty, weekly hours, and warnings. Save or download your plan.

Plans are stored in `.runtime/predictor.sqlite3`, created automatically. Saved plans are shown for the current browser session; download JSON to keep a portable copy.

## Features

- Browse 492 courses, including 467 GE options.
- Check prerequisites, estimate difficulty and weekly workload, and flag heavy course combinations.
- Save plans locally or download them as JSON.

Scores are rough estimates. Some prerequisites need manual review, and course availability is not checked. Download plans to keep a copy across browser sessions.

## Project files

- `app.py` — user interface.
- `predictor/` — eligibility, scoring, and database code.
- `backend/database/` — Joseph's database schema and setup script, retained for later integration; the app currently uses `predictor/repository.py`.
- `data/sjsu/2026-2027/` — course dataset and sources.
- `scripts/build_dataset.py` — rebuilds the dataset from saved catalog sources.
- `tests/` — app and logic tests.

See [data notes](docs/DATA.md) and [Joseph's backend integration notes](docs/INTEGRATION.md) for details.

## Tests

```sh
pip install -r requirements-dev.txt
python -m pytest -q
```

Tests cover catalog data, eligibility rules, scoring, database storage, and the main UI flows.

If the app's port is busy, run `streamlit run app.py --server.port 8502`. Press **Ctrl+C** to stop the server.

## Documentation

Add short docstrings for classes and functions, and comments for tricky logic. This applies to AI-generated code too.

## AI-Assisted Development

- **Tool used:** OpenAI Codex.
- **Help provided:** Catalog data collection, the Streamlit interface, eligibility checks, workload estimates, local database code, tests, and documentation.
- **Example correction:** The initial UI tests reused Streamlit's cached database setup between tests, causing a “no such table” error. Clearing the cache before each test fixed the issue.
- **Human decision:** The team chose to focus the MVP on SJSU's Software Engineering major. Will also requested a simpler interface after reviewing the first version.
