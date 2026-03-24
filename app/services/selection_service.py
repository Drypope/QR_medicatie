from __future__ import annotations

from typing import Any, MutableMapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MedicationCatalog, Preset
from app.services.selection_state import add_catalog_item_to_selection, load_preset_into_session


def load_preset_selection(session: Session, session_state: MutableMapping[str, Any], preset_id: int) -> list[dict[str, Any]]:
    preset = session.scalar(select(Preset).where(Preset.id == preset_id))
    if preset is None:
        raise ValueError(f"Preset not found: {preset_id}")

    preset_items: list[dict[str, Any]] = []
    for item in preset.items:
        preset_items.append(
            {
                "id": item.catalog.id,
                "product_class": item.catalog.product_class,
                "product_name": item.catalog.product_name,
                "unique_id": item.catalog.unique_id,
                "quantity": int(item.default_quantity),
            }
        )
    return load_preset_into_session(session_state, preset_items)


def add_catalog_item(session: Session, session_state: MutableMapping[str, Any], catalog_id: int) -> list[dict[str, Any]]:
    catalog_item = session.scalar(select(MedicationCatalog).where(MedicationCatalog.id == catalog_id))
    if catalog_item is None:
        raise ValueError(f"Catalog item not found: {catalog_id}")

    return add_catalog_item_to_selection(
        session_state,
        catalog_id=catalog_item.id,
        product_class=catalog_item.product_class,
        product_name=catalog_item.product_name,
        unique_id=catalog_item.unique_id,
        quantity=1,
    )
