# AGENTS.md

## Project name
MedMatrix

## Purpose
Build a small Windows-friendly medication barcode application for hospital use.

Version 1 is a **local app with a browser UI**:
- launched locally, potentially from a shared Windows folder
- opens in Chrome
- serves a web UI from a local FastAPI server on `127.0.0.1`
- reads medication catalog and presets from editable files
- stores runtime database data locally on each machine
- generates a **Data Matrix** barcode from selected medications

The codebase must be structured so it can later be deployed as a **hosted FastAPI web app** with minimal rework.

---

## Product scope for v1

### Core features
- Show a two-column UI in the browser
- Left side:
  - preset selector
  - selected medications grouped by `product_class`
  - each group header has a `+` action to add a medication from that class
  - each medication row has:
    - decrement button
    - quantity display
    - increment button
    - delete icon
    - medication name
- Right side:
  - rendered Data Matrix image
  - large `Generate` button below it
  - optional raw payload preview below the image
- Load medication definitions from a file-based source
- Load presets from a file-based source
- Generate final payload string from current selection
- Render Data Matrix locally in the app

### Explicit non-goals for v1
Do not implement these unless explicitly asked:
- authentication or SSO
- public internet deployment
- multi-user shared database
- Google Sheets integration
- scanner integration
- printing workflows
- role-based permissions
- admin preset editor UI
- write-back to the source files

---

## Fixed technical decisions

Use these unless explicitly changed by the user:
- Python 3.10
- FastAPI
- Jinja2 templates
- lightweight vanilla JavaScript
- SQLAlchemy with SQLite
- `pylibdmtx` + Pillow for Data Matrix generation
- PyInstaller one-folder build for Windows

### Important constraints
- This project needs **Data Matrix**, not QR code
- SQLite must be **local to each machine**
- Never store the SQLite database on a shared Windows/network folder
- Shared folder usage is allowed for:
  - executable distribution
  - editable source files like catalog and presets
- The UI should work in Chrome
- The app should run on localhost in v1
- The app must be designed so future migration to a hosted server deployment is easy

---

## Runtime model

### Version 1
The app is a local web app:
1. user launches the app locally
2. app starts FastAPI/Uvicorn on `127.0.0.1:<port>`
3. app opens Chrome to the local URL
4. app syncs source files into a local SQLite cache
5. user interacts through the browser UI

### Future version
The same app should be deployable as a hosted web app:
- reverse proxy in front
- remote database later if needed
- no automatic browser opening
- different config, same app structure

Keep application logic deployment-neutral.

---

## Source data for v1

### Catalog source
Preferred file: `catalog.xlsx`

Expected sheet name:
- `catalog`

Required columns:
- `product_class`
- `product_name`
- `unique_id`

Optional columns:
- `sort_order`
- `is_active`
- `short_name`

### Preset source
Preferred file: `presets.json`

Example structure:
```json
{
  "presets": [
    {
      "name": "OR induction basic",
      "description": "Basic induction set",
      "items": [
        { "product_name": "Propofol 1% 20mL", "quantity": 2 },
        { "product_name": "Rocuronium 50mg/5mL", "quantity": 1 }
      ]
    }
  ]
}
