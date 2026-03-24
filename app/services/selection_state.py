from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import Any, MutableMapping

SelectionItem = dict[str, Any]
SESSION_KEY = "selection"


def _sort_selection(items: list[SelectionItem]) -> list[SelectionItem]:
    return sorted(
        items,
        key=lambda item: (
            str(item["product_class"]).lower(),
            str(item["product_name"]).lower(),
            str(item["unique_id"]),
            int(item["id"]),
        ),
    )


def get_selection(session_state: MutableMapping[str, Any]) -> list[SelectionItem]:
    raw = session_state.get(SESSION_KEY, [])
    if not isinstance(raw, list):
        return []
    normalized: list[SelectionItem] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        quantity = int(item.get("quantity", 0))
        if quantity <= 0:
            continue
        normalized.append(
            {
                "id": int(item["id"]),
                "product_class": str(item["product_class"]),
                "product_name": str(item["product_name"]),
                "unique_id": str(item["unique_id"]),
                "quantity": quantity,
            }
        )
    return _sort_selection(normalized)


def set_selection(session_state: MutableMapping[str, Any], selection: list[SelectionItem]) -> list[SelectionItem]:
    sorted_selection = _sort_selection(selection)
    session_state[SESSION_KEY] = deepcopy(sorted_selection)
    return sorted_selection


def load_preset_into_session(session_state: MutableMapping[str, Any], preset_items: list[SelectionItem]) -> list[SelectionItem]:
    return set_selection(session_state, preset_items)


def add_catalog_item_to_selection(
    session_state: MutableMapping[str, Any],
    *,
    catalog_id: int,
    product_class: str,
    product_name: str,
    unique_id: str,
    quantity: int = 1,
) -> list[SelectionItem]:
    selection = get_selection(session_state)
    for item in selection:
        if item["id"] == catalog_id:
            item["quantity"] += max(quantity, 1)
            return set_selection(session_state, selection)

    selection.append(
        {
            "id": catalog_id,
            "product_class": product_class,
            "product_name": product_name,
            "unique_id": unique_id,
            "quantity": max(quantity, 1),
        }
    )
    return set_selection(session_state, selection)


def increment_selected_item(session_state: MutableMapping[str, Any], catalog_id: int) -> list[SelectionItem]:
    selection = get_selection(session_state)
    for item in selection:
        if item["id"] == catalog_id:
            item["quantity"] += 1
            break
    return set_selection(session_state, selection)


def decrement_selected_item(session_state: MutableMapping[str, Any], catalog_id: int) -> list[SelectionItem]:
    selection = get_selection(session_state)
    kept: list[SelectionItem] = []
    for item in selection:
        if item["id"] == catalog_id:
            new_qty = item["quantity"] - 1
            if new_qty > 0:
                item["quantity"] = new_qty
                kept.append(item)
            continue
        kept.append(item)
    return set_selection(session_state, kept)


def delete_selected_item(session_state: MutableMapping[str, Any], catalog_id: int) -> list[SelectionItem]:
    selection = [item for item in get_selection(session_state) if item["id"] != catalog_id]
    return set_selection(session_state, selection)


def group_selected_by_product_class(items: list[SelectionItem]) -> dict[str, list[SelectionItem]]:
    grouped: dict[str, list[SelectionItem]] = defaultdict(list)
    for item in _sort_selection(items):
        grouped[item["product_class"]].append(item)
    return {product_class: grouped[product_class] for product_class in sorted(grouped.keys(), key=str.lower)}
