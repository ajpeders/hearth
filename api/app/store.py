"""Tiny JSON persistence for hearth's state (timers, shopping list).

Everything lives in HEARTH_DATA_DIR on the device — hearth is 100% offline, so
local disk *is* the database.
"""
import json
import os
import threading
from pathlib import Path

DATA_DIR = Path(os.environ.get("HEARTH_DATA_DIR", "./data"))
_lock = threading.Lock()


def load(name: str, default):
    try:
        return json.loads((DATA_DIR / f"{name}.json").read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save(name: str, value) -> None:
    with _lock:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / f"{name}.json").write_text(json.dumps(value, indent=2))
