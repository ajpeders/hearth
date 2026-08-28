"""Timers, shopping list, and the companion mount (fake provider — offline
even in tests)."""
import json
import os
import tempfile

os.environ["HEARTH_DATA_DIR"] = tempfile.mkdtemp(prefix="hearth-test-")

import pytest
from fastapi.testclient import TestClient

from companion import Completion
from app import store
from app.main import app


@pytest.fixture()
def client(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    return TestClient(app)


def test_timer_lifecycle(client):
    t = client.post("/api/timers", json={"label": "pasta", "seconds": 600}).json()
    assert t["label"] == "pasta" and 598 <= t["remainingSeconds"] <= 600 and not t["ringing"]
    assert [x["id"] for x in client.get("/api/timers").json()] == [t["id"]]
    assert client.delete(f"/api/timers/{t['id']}").json() == {"ok": True}
    assert client.get("/api/timers").json() == []
    assert client.delete("/api/timers/nope").status_code == 404


def test_shopping_list(client):
    a = client.post("/api/shopping/items", json={"name": "parmesan"}).json()
    client.post("/api/shopping/items", json={"name": "eggs"})
    assert [i["name"] for i in client.get("/api/shopping").json()] == ["parmesan", "eggs"]
    client.delete(f"/api/shopping/items/{a['id']}")
    assert client.delete("/api/shopping").json() == {"removed": 1}
    assert client.get("/api/shopping").json() == []


def test_mount_tool_classification(client):
    tools = {t["name"]: t for t in client.get("/api/companion/manifest").json()["tools"]}
    # benign actions auto-run (reclassified as reads) so voice never stalls
    assert tools["post_api_timers"]["access"] == "read"
    assert tools["post_api_shopping_items"]["access"] == "read"
    assert tools["delete_api_timers_by_timer_id"]["access"] == "read"
    # nuking the whole list stays confirm-gated
    assert tools["delete_api_shopping"]["access"] == "write"
    assert "post_api_transcribe" not in tools


def test_chat_flow_with_scripted_provider(client, monkeypatch):
    """Tool turn -> auto-executed read -> final text. (Loopback execution against
    a real server is covered by the live E2E script, not here.)"""
    from companion import ToolCall
    from companion.providers.ollama import OllamaProvider

    script = [
        Completion(tool_calls=[ToolCall(id="1", name="post_api_shopping_items",
                                        arguments={"name": "olive oil"})]),
        Completion(text="Added olive oil."),
    ]

    async def fake(self, *, system, messages, tools=None):
        assert "kitchen counter" in system  # skill file loaded
        return script.pop(0)

    monkeypatch.setattr(OllamaProvider, "complete_text", fake)
    monkeypatch.setattr(OllamaProvider, "stream_text", None)  # force buffered path
    r = client.post("/api/companion/chat", json={"messages": [
        {"role": "user", "content": "add olive oil to the list"}]})
    events = [json.loads(l[6:]) for l in r.text.splitlines() if l.startswith("data: ")]
    assert [e["type"] for e in events] == ["tool_call", "tool_result", "text", "done"]
    assert events[2]["text"] == "Added olive oil."
