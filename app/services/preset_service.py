from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MedicationCatalog, Preset, PresetItem


def sync_presets(session: Session, presets_path: Path) -> int:
    if not presets_path.exists():
        return 0

    payload = json.loads(presets_path.read_text(encoding="utf-8"))
    preset_defs = payload.get("presets", [])

    catalog_by_name = {
        item.product_name: item
        for item in session.scalars(select(MedicationCatalog).where(MedicationCatalog.is_active.is_(True))).all()
    }

    count = 0
    unknown_medications: list[str] = []

    for p in preset_defs:
        name = str(p.get("name", "")).strip()
        if not name:
            continue
        preset = session.scalar(select(Preset).where(Preset.name == name))
        if preset is None:
            preset = Preset(name=name, description=str(p.get("description", "")))
            session.add(preset)
            session.flush()
        else:
            preset.description = str(p.get("description", ""))
            preset.items.clear()

        for item in p.get("items", []):
            product_name = str(item.get("product_name", "")).strip()
            quantity = int(item.get("quantity", 1))
            catalog = catalog_by_name.get(product_name)
            if catalog is None:
                unknown_medications.append(f"{name}: {product_name}")
                continue
            preset.items.append(PresetItem(catalog_id=catalog.id, default_quantity=max(quantity, 1)))

        count += 1

    if unknown_medications:
        session.rollback()
        unknown_list = ", ".join(sorted(set(unknown_medications)))
        raise ValueError(f"Presets reference unknown medications: {unknown_list}")

    session.commit()
    return count
