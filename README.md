# MedMatrix

Initial scaffold for a local FastAPI + Jinja2 Data Matrix medication app.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

## Tests

```bash
pytest
```
