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


If the exact layout changes slightly, preserve the same separation of concerns.

Data model expectations

Use SQLAlchemy models for local SQLite.

Expected tables:

medication_catalog

Fields:

id
product_class
product_name
unique_id
sort_order
is_active
source_hash
source_updated_at
last_synced_at
presets

Fields:

id
name
description
preset_items

Fields:

id
preset_id
catalog_id
default_quantity
Optional later

generated_payloads

only add when useful
do not over-engineer audit/history early
UI requirements
Main page

Two-column layout:

left panel for preset and selected medications
right panel for Data Matrix output and Generate button
Interaction style

Keep frontend simple:

plain HTML templates
lightweight JavaScript only
no React, no SPA framework, no frontend build pipeline
User interactions

Support:

load preset
increment item quantity
decrement item quantity
delete item
add item within a medication class
generate barcode
UX expectations
clear, uncluttered interface
predictable ordering
obvious actions
good error messages
no unnecessary popups
Config requirements

Config must support both local mode and future hosted mode.

Expected settings include:

APP_MODE
HOST
PORT
LOCAL_DATA_DIR
SHARED_SOURCE_DIR
CATALOG_FILE
PRESETS_FILE
DATABASE_URL
AUTO_OPEN_BROWSER
Local mode rules
bind to 127.0.0.1
local DB under %LOCALAPPDATA%\MedMatrix\
shared source files may live elsewhere
Future hosted mode rules
bind address and DB must be configurable
do not embed local-only assumptions into business logic
Session/state rules

For v1:

keep current working selection in session or simple server-side state
do not persist every click to the database
database is for catalog/preset storage, not transient editing state

Keep state handling simple and replaceable.

Implementation rules
Code quality
prefer small typed modules
prefer explicit names over clever abstractions
keep route handlers thin
keep business logic in services
avoid duplicated logic
write code that is easy to migrate later
Dependencies
keep dependencies minimal
avoid large frontend frameworks
avoid Windows-specific code outside launcher/packaging areas
do not add Google APIs unless explicitly requested later
Error handling

Handle gracefully:

missing source files
malformed Excel/JSON
duplicate or ambiguous product names
missing unique_id
barcode generation failure
localhost port already in use

Return useful errors for both users and developers.

Testing expectations

Tests are required.

Priority tests
payload builder tests
catalog sync tests
preset resolution tests
Data Matrix service tests
UI route tests
Payload builder must be heavily tested

Cover:

empty selection
single item
repeated quantity
deterministic ordering
missing or invalid data
inactive items excluded if applicable
General testing rule

Test business logic before polishing UI behavior.

Packaging requirements

Version 1 must be packageable for Windows with PyInstaller.

Packaging rules
prefer one-folder build
include templates/static assets
keep editable source files external
keep local DB outside the packaged app directory
do not assume write access to the shared folder
Launch behavior

The launcher should:

create local app data directory if needed
initialize DB if needed
sync source data
start server
open Chrome or default browser to local URL
Definition of done for v1

A task is only complete when:

code is in the right architectural layer
tests for core logic exist and pass
behavior matches the business rules above
no shared-folder SQLite writes are introduced
no unnecessary complexity is added
the result still supports future migration to hosted mode
Recommended build order

When implementing from scratch, use this order:

scaffold project structure
config and database setup
catalog and preset import
repository interfaces and implementations
selection and payload builder services
Data Matrix service
UI routes and templates
tests
local launcher
packaging
What not to do

Do not:

convert this into a desktop GUI toolkit app
use QR code libraries instead of Data Matrix
store SQLite on a network share
overbuild authentication/admin features in v1
introduce React/Node unless explicitly requested
hardcode paths specific to one machine
tie business logic directly to Excel parsing code
skip tests for payload logic
How to work in this repo

Before making major changes:

read this file
inspect existing folder structure
preserve architectural separation
prefer incremental commits/changes
summarize what is implemented vs stubbed

When asked to scaffold:

create the structure first
stub modules cleanly
implement core logic in small steps
report what remains

When unsure:

choose the simpler design that preserves future migration flexibility
do not silently expand scope
