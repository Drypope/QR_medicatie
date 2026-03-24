from collections import defaultdict


def group_selection(items: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        grouped[item["product_class"]].append(item)
    return dict(grouped)
