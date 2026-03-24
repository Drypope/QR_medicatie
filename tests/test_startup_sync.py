import json
from pathlib import Path

from openpyxl import Workbook
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import Base
from app.models import MedicationCatalog, Preset
from app.services.startup_sync import sync_source_files


def _write_catalog(path: Path):
    wb = Workbook()
    ws = wb.active
    ws.title = "catalog"
    ws.append(["product_class", "product_name", "unique_id", "sort_order", "is_active"])
    ws.append(["Induction", "Propofol", "P001", 10, True])
    wb.save(path)


def test_sync_source_files_loads_catalog_and_presets(tmp_path: Path):
    catalog_path = tmp_path / "catalog.xlsx"
    presets_path = tmp_path / "presets.json"
    _write_catalog(catalog_path)
    presets_path.write_text(
        json.dumps(
            {
                "presets": [
                    {
                        "name": "OR basic",
                        "description": "basic",
                        "items": [{"product_name": "Propofol", "quantity": 2}],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    old_catalog_path = settings.catalog_path
    old_presets_path = settings.presets_path
    settings.catalog_file = catalog_path.name
    settings.presets_file = presets_path.name
    settings.shared_source_dir = tmp_path

    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    try:
        with Session(engine) as session:
            catalog_count, preset_count = sync_source_files(session)
            assert catalog_count == 1
            assert preset_count == 1

            assert session.scalar(select(MedicationCatalog).where(MedicationCatalog.product_name == "Propofol")) is not None
            preset = session.scalar(select(Preset).where(Preset.name == "OR basic"))
            assert preset is not None
            assert len(preset.items) == 1
    finally:
        settings.shared_source_dir = old_catalog_path.parent
        settings.catalog_file = old_catalog_path.name
        settings.presets_file = old_presets_path.name
