"""Kitchen timers — the bread-and-butter tool. Multiple named timers; remaining
time computed on read; expired timers stay listed (ringing) until dismissed."""
import time
import uuid

from .store import load, save


def _all() -> list[dict]:
    return load("timers", [])


def create(label: str, seconds: int) -> dict:
    t = {
        "id": uuid.uuid4().hex[:8],
        "label": label or "timer",
        "seconds": seconds,
        "endsAt": time.time() + seconds,
    }
    timers = _all()
    timers.append(t)
    save("timers", timers)
    return status(t)


def status(t: dict) -> dict:
    remaining = max(0, int(round(t["endsAt"] - time.time())))
    return {
        "id": t["id"],
        "label": t["label"],
        "seconds": t["seconds"],
        "remainingSeconds": remaining,
        "ringing": remaining == 0,
    }


def list_timers() -> list[dict]:
    return [status(t) for t in _all()]


def dismiss(timer_id: str) -> bool:
    timers = _all()
    kept = [t for t in timers if t["id"] != timer_id]
    if len(kept) == len(timers):
        return False
    save("timers", kept)
    return True
