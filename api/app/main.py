"""hearth — an offline kitchen voice assistant. FastAPI host app + companion.

Everything runs on the device: Ollama at localhost for the LLM, faster-whisper
for ears, JSON files for state. No internet in the loop, by design.
"""
import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from . import shopping, timers, voice

app = FastAPI(title="hearth")


@app.get("/api/health")
async def health() -> dict:
    return {"ok": True, "voice": voice.available()}


# ---- timers -----------------------------------------------------------------
class TimerIn(BaseModel):
    label: str = "timer"
    seconds: int = Field(gt=0, le=24 * 3600)


@app.post("/api/timers", status_code=201)
async def create_timer(t: TimerIn) -> dict:
    """Start a named kitchen timer (e.g. label 'pasta', seconds 600)."""
    return timers.create(t.label, t.seconds)


@app.get("/api/timers")
async def list_timers() -> list[dict]:
    """List running timers with remaining seconds; ringing=true means done."""
    return timers.list_timers()


@app.delete("/api/timers/{timer_id}")
async def dismiss_timer(timer_id: str) -> dict:
    """Dismiss (stop/silence) a timer by id."""
    if not timers.dismiss(timer_id):
        raise HTTPException(status_code=404, detail="No such timer.")
    return {"ok": True}


# ---- shopping list ----------------------------------------------------------
class ItemIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)


@app.get("/api/shopping")
async def shopping_list() -> list[dict]:
    """The current shopping list."""
    return shopping.list_items()


@app.post("/api/shopping/items", status_code=201)
async def add_item(item: ItemIn) -> dict:
    """Add one item to the shopping list."""
    return shopping.add(item.name)


@app.delete("/api/shopping/items/{item_id}")
async def remove_item(item_id: str) -> dict:
    """Remove one item from the shopping list by id."""
    if not shopping.remove(item_id):
        raise HTTPException(status_code=404, detail="No such item.")
    return {"ok": True}


@app.delete("/api/shopping")
async def clear_list() -> dict:
    """Clear the ENTIRE shopping list. Destructive."""
    return {"removed": shopping.clear()}


# ---- ears -------------------------------------------------------------------
@app.post("/api/transcribe")
async def transcribe(audio: UploadFile = File(...)) -> dict:
    """Speech-to-text, fully on-device. Audio is processed and discarded."""
    if not voice.available():
        raise HTTPException(status_code=501, detail="Install hearth[voice] for STT.")
    data = await audio.read()
    if len(data) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio too large.")
    suffix = os.path.splitext(audio.filename or "a.wav")[1] or ".wav"
    return {"text": voice.transcribe(data, suffix)}


# ---- companion mount --------------------------------------------------------
# Offline by construction: the provider is the device's own Ollama. Benign
# actions (start/dismiss timer, add/remove one item) are reclassified as reads
# so voice flows don't stall on confirmations; only clearing the whole list
# stays confirm-gated. Boundaries are documented in ARCHITECTURE.md.
from companion import Companion, OllamaProvider  # noqa: E402

_companion = Companion(
    host_app=app,
    base_url=os.environ.get("HEARTH_SELF_BASE_URL", "http://127.0.0.1:8600"),
    expose=["GET /api/timers*", "POST /api/timers", "DELETE /api/timers/*",
            "GET /api/shopping*", "POST /api/shopping/items",
            "DELETE /api/shopping*"],
    exclude=["* /api/transcribe*", "* /api/health*"],
    reads=["POST /api/timers", "DELETE /api/timers/*",
           "POST /api/shopping/items", "DELETE /api/shopping/items/*"],
    default_provider=OllamaProvider(
        base_url=os.environ.get("HEARTH_OLLAMA_URL", "http://127.0.0.1:11434"),
        model=os.environ.get("HEARTH_MODEL", "qwen3:8b"),
        think=False,  # spoken replies need to come back in seconds
    ),
    skills_dir=os.path.join(os.path.dirname(__file__), "skills"),
    write_policy="confirm",
    forward_auth=(),  # single-user device, no auth to forward
    mount_prefix="/api/companion",
    tool_timeout=15.0,
)
app.include_router(_companion.router, prefix="/api/companion")
