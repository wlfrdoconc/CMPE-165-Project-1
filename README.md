# Semester Compass

A semester difficulty predictor for SJSU Software Engineering students. Built with Python, Streamlit, and SQLite using the 2026–2027 catalog.

## Run

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open [localhost:8501](http://localhost:8501) and click **Load sample student** to try it.

## Features

- Browse 492 courses, including 467 GE options.
- Check prerequisites and estimate difficulty and weekly workload.
- Save plans locally or download them as JSON.

Scores are rough estimates. Some prerequisites need manual review, and course availability is not checked. Download plans to keep a copy across browser sessions.

## Project files

- `app.py` — user interface.
- `predictor/` — eligibility, scoring, and database code.
- `data/sjsu/2026-2027/` — course dataset and sources.
- `tests/` — app and logic tests.

See [data notes](docs/DATA.md) and [Joseph's backend integration notes](docs/INTEGRATION.md) for details.

## Tests

```sh
pip install -r requirements-dev.txt
python -m pytest -q
```

## Documentation

Add short docstrings for classes and functions, and comments for tricky logic. This applies to AI-generated code too.
