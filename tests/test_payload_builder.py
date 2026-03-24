import pytest

from app.services.payload_builder import SelectedItem, build_payload


def test_build_payload_empty_selection_returns_empty_string():
    assert build_payload([]) == ""


def test_build_payload_single_item():
    payload = build_payload([SelectedItem(unique_id="A1", product_name="Alpha", quantity=1, product_class="A")])
    assert payload == "A1:1"


def test_build_payload_ignores_zero_quantities():
    payload = build_payload([
        SelectedItem(unique_id="A1", product_name="Alpha", quantity=0, product_class="A"),
        SelectedItem(unique_id="B1", product_name="Beta", quantity=2, product_class="B"),
    ])
    assert payload == "B1:2"


def test_build_payload_is_deterministic_by_class_then_name_then_id():
    payload = build_payload([
        SelectedItem(unique_id="Z9", product_name="Zulu", quantity=1, product_class="ClassB"),
        SelectedItem(unique_id="A1", product_name="Alpha", quantity=3, product_class="ClassA"),
    ])
    assert payload == "A1:3|Z9:1"


def test_build_payload_raises_for_missing_unique_id():
    with pytest.raises(ValueError):
        build_payload([SelectedItem(unique_id="", product_name="Alpha", quantity=1, product_class="A")])
