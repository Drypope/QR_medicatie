# MedMatrix

Local FastAPI + Jinja2 application for medication selection and Data Matrix generation.

## Requirements

- Python 3.10
- Local editable source files:
  - `catalog.xlsx` with a `catalog` sheet
  - `presets.json`

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765` in Chrome.

## Source-file sync and refresh

- On app startup, MedMatrix syncs `catalog.xlsx` and `presets.json` into local SQLite.
- Use the **Refresh sources** button in the UI to rerun sync manually.
- Friendly in-app errors are shown when:
  - `catalog.xlsx` is missing or malformed
  - `presets.json` references unknown medications

## Run tests

```bash
pytest -q
```

Notes:
- Data Matrix render test may be skipped if native `libdmtx` is unavailable.
