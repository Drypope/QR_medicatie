from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.models import MedicationCatalog, Preset, PresetItem
from app.services.selection_service import load_preset_selection


def test_load_preset_selection_uses_preset_items_default_quantity_and_sorted_order():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        med_b = MedicationCatalog(product_class="B", product_name="Beta", unique_id="B001", is_active=True)
        med_a = MedicationCatalog(product_class="A", product_name="Alpha", unique_id="A001", is_active=True)
        session.add_all([med_b, med_a])
        session.flush()

        preset = Preset(name="Preset 1", description="Test")
        session.add(preset)
        session.flush()

        # Insert in reverse sorted order to verify service + state sorting.
        session.add(PresetItem(preset_id=preset.id, catalog_id=med_b.id, default_quantity=1))
        session.add(PresetItem(preset_id=preset.id, catalog_id=med_a.id, default_quantity=3))
        session.commit()

        session_state: dict = {}
        loaded = load_preset_selection(session, session_state, preset.id)

        assert [item["product_name"] for item in loaded] == ["Alpha", "Beta"]
        assert [item["quantity"] for item in loaded] == [3, 1]
        assert session_state["selection"] == loaded
