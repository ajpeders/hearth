# hearth

An **offline kitchen voice assistant** — a secure, better Alexa that sits on
the kitchen counter and runs **100% on-device**: local Ollama for the brain,
faster-whisper for ears, JSON files for state. No cloud, no account, no
internet in the loop. Built as a host app for the reusable
[`companion`](../companion/) package: the assistant's abilities are its own
REST endpoints, exposed to the model as tools.

## What it does (v1)

- **Kitchen timers** — multiple, named, by voice ("set a pasta timer for ten
  minutes"), queried ("how long left?"), dismissed.
- **Shopping list** — add/remove while cooking, read back at the store.
- **Speech-to-text** — `POST /api/transcribe` (faster-whisper, on-device,
  audio discarded after transcription).
- Benign actions run instantly; destructive ones (clear the whole list)
  pause for confirmation.

## Quick start

```sh
cd api && python -m venv .venv && .venv/bin/pip install -e ".[voice,dev]"
ollama pull qwen3:8b                       # the local brain
.venv/bin/uvicorn app.main:app --port 8600
# then: POST /api/companion/chat {"messages":[{"role":"user","content":"set a pasta timer for 10 minutes"}]}
```

Config (env): `HEARTH_OLLAMA_URL` (default `http://127.0.0.1:11434`),
`HEARTH_MODEL` (default `qwen3:8b`), `HEARTH_WHISPER_MODEL` (default `small`),
`HEARTH_DATA_DIR`, `HEARTH_SELF_BASE_URL` (default `http://127.0.0.1:8600`).

## Key commands

```sh
.venv/bin/pytest                # tests (offline, fake provider)
curl localhost:8600/api/health  # {"ok": true, "voice": true|false}
curl localhost:8600/api/companion/manifest   # what the model can do
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for design + trust boundaries,
[ROADMAP.md](ROADMAP.md) for status, [HOWTO.md](HOWTO.md) for guides.
