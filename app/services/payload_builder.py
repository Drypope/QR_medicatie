from dataclasses import dataclass


@dataclass(frozen=True)
class SelectedItem:
    unique_id: str
    product_name: str
    quantity: int
    product_class: str = ""


def build_payload(items: list[SelectedItem]) -> str:
    normalized: list[SelectedItem] = []
    for item in items:
        if item.quantity <= 0:
            continue
        if not item.unique_id.strip():
            raise ValueError(f"Missing unique_id for {item.product_name}")
        normalized.append(item)

    if not normalized:
        return ""

    ordered = sorted(normalized, key=lambda i: (i.product_class.lower(), i.product_name.lower(), i.unique_id))
    return "|".join(f"{item.unique_id}:{item.quantity}" for item in ordered)
