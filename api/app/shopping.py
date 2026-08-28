"""Shopping list — add while cooking, read back at the store."""
import uuid

from .store import load, save


def list_items() -> list[dict]:
    return load("shopping", [])


def add(name: str) -> dict:
    item = {"id": uuid.uuid4().hex[:8], "name": name.strip()}
    items = list_items()
    items.append(item)
    save("shopping", items)
    return item


def remove(item_id: str) -> bool:
    items = list_items()
    kept = [i for i in items if i["id"] != item_id]
    if len(kept) == len(items):
        return False
    save("shopping", kept)
    return True


def clear() -> int:
    n = len(list_items())
    save("shopping", [])
    return n
