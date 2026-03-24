from app.services.selection_state import (
    add_catalog_item_to_selection,
    decrement_selected_item,
    delete_selected_item,
    get_selection,
    group_selected_by_product_class,
    increment_selected_item,
    load_preset_into_session,
)


def test_load_preset_into_session_sets_selection_shape():
    session = {}
    preset_items = [
        {
            "id": 1,
            "product_class": "Induction",
            "product_name": "Propofol",
            "unique_id": "P001",
            "quantity": 2,
        }
    ]

    result = load_preset_into_session(session, preset_items)

    assert result == preset_items
    assert get_selection(session) == preset_items


def test_add_catalog_item_to_selection_increments_existing_item():
    session = {}
    add_catalog_item_to_selection(
        session,
        catalog_id=1,
        product_class="Induction",
        product_name="Propofol",
        unique_id="P001",
        quantity=1,
    )

    result = add_catalog_item_to_selection(
        session,
        catalog_id=1,
        product_class="Induction",
        product_name="Propofol",
        unique_id="P001",
        quantity=1,
    )

    assert result[0]["quantity"] == 2


def test_increment_decrement_and_delete_selection_item():
    session = {
        "selection": [
            {
                "id": 1,
                "product_class": "Induction",
                "product_name": "Propofol",
                "unique_id": "P001",
                "quantity": 2,
            }
        ]
    }

    increment_selected_item(session, 1)
    assert get_selection(session)[0]["quantity"] == 3

    decrement_selected_item(session, 1)
    assert get_selection(session)[0]["quantity"] == 2

    decrement_selected_item(session, 1)
    decrement_selected_item(session, 1)
    assert get_selection(session) == []

    add_catalog_item_to_selection(
        session,
        catalog_id=2,
        product_class="Relaxant",
        product_name="Rocuronium",
        unique_id="R001",
        quantity=1,
    )
    delete_selected_item(session, 2)
    assert get_selection(session) == []


def test_group_selected_by_product_class():
    items = [
        {"id": 1, "product_class": "A", "product_name": "One", "unique_id": "1", "quantity": 1},
        {"id": 2, "product_class": "A", "product_name": "Two", "unique_id": "2", "quantity": 1},
        {"id": 3, "product_class": "B", "product_name": "Three", "unique_id": "3", "quantity": 1},
    ]

    grouped = group_selected_by_product_class(items)

    assert list(grouped.keys()) == ["A", "B"]
    assert [item["id"] for item in grouped["A"]] == [1, 2]
