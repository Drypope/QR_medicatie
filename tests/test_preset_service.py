import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db import Base
from app.models import MedicationCatalog, Preset
from app.services.preset_service import sync_presets


def test_sync_presets_resolves_catalog_items(tmp_path: Path):
    presets_path = tmp_path / "presets.json"
    presets_path.write_text(json.dumps({
        "presets": [
            {
                "name": "OR basic",
                "description": "Basic",
                "items": [{"product_name": "Propofol", "quantity": 2}],
            }
        ]
    }))

    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(MedicationCatalog(product_class="Induction", product_name="Propofol", unique_id="P001"))
        session.commit()

        count = sync_presets(session, presets_path)
        assert count == 1

        preset = session.scalar(select(Preset).where(Preset.name == "OR basic"))
        assert preset is not None
        assert len(preset.items) == 1
        assert preset.items[0].default_quantity == 2


def test_sync_presets_raises_for_unknown_medications(tmp_path: Path):
    presets_path = tmp_path / "presets.json"
    presets_path.write_text(json.dumps({
        "presets": [
            {
                "name": "OR bad",
                "description": "Bad",
                "items": [{"product_name": "Unknown Med", "quantity": 1}],
            }
        ]
    }))

    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        with pytest.raises(ValueError, match="unknown medications"):
            sync_presets(session, presets_path)
