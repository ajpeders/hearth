# hearth — how to

## Run it on a MacBook

```sh
# 1. brain: install Ollama (ollama.com) and pull the model
ollama pull qwen3:8b

# 2. api
cd api && python -m venv .venv && .venv/bin/pip install -e ".[voice,dev]"
.venv/bin/uvicorn app.main:app --port 8600

# 3. sanity
curl localhost:8600/api/health        # voice:true means whisper is ready
```

## Talk to it (no client yet)

```sh
curl -N localhost:8600/api/companion/chat -H 'content-type: application/json' \
  -d '{"messages":[{"role":"user","content":"set a pasta timer for 10 minutes"}]}'
```

## Voice round-trip by hand

```sh
# record 5s (macOS: sox via `brew install sox`)
rec -c 1 -r 16000 ask.wav trim 0 5
curl -F audio=@ask.wav localhost:8600/api/transcribe   # -> {"text": "..."}
# feed that text into the chat call above; speak the reply:
say "Pasta timer set, ten minutes."
```

## Approve a destructive action

A `confirm` SSE event means the model wants a gated tool (e.g. clear the whole
list). Re-POST `/api/companion/chat` with the event's `messages` array plus
`"approvals": {"<event id>": true}` — the loop resumes and executes it.

## Change model / whisper size

`HEARTH_MODEL=qwen3:8b` (any Ollama tool-capable model),
`HEARTH_WHISPER_MODEL=small|base|medium`. Restart uvicorn after changing.

## Run tests

```sh
cd api && .venv/bin/pytest
```
