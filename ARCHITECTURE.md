# hearth — architecture

## Shape

```
device (MacBook / kitchen box)
├─ hearth api (FastAPI, :8600)
│   ├─ /api/timers*, /api/shopping*     ← the assistant's abilities
│   ├─ /api/transcribe                  ← faster-whisper STT (on-device)
│   └─ /api/companion/*                 ← companion mount (chat loop)
│         tools = hearth's own endpoints, via loopback HTTP
├─ Ollama (:11434)                      ← qwen3:8b, think=False
└─ client: push-to-talk → /api/transcribe → /api/companion/chat (SSE) → TTS
```

hearth follows the companion host-app pattern (like gym-app and docuAI): all
domain logic — timers, lists, voice — lives here; companion contributes only
the provider seam, the tool loop, and the SSE chat contract. Config is the
**per-app** pattern: one `default_provider` pointed at the device's Ollama.

## Data flow (one voice interaction)

1. Client records while the button is held, POSTs audio to `/api/transcribe`.
2. Whisper transcribes on-device; audio bytes are discarded, never stored.
3. Transcript goes to `/api/companion/chat` as the user message.
4. Model (local Ollama) calls tools — real loopback HTTP against hearth's own
   API — and returns a short spoken-style reply, streamed as SSE events.
5. Client speaks the reply (TTS — roadmap) and shows/rings timers.

## Trust boundaries (the point of the product)

- **Offline by construction.** LLM, STT, and state are all on-device. The
  process makes no network calls beyond localhost. There is deliberately no
  BYO-cloud-key resolver here — plugging a cloud provider into a
  microphone-bearing device is a different product; if ever added, it must be
  a visible, per-conversation, opt-in choice.
- **Audio is ephemeral.** Bytes in → text out → discarded. Nothing is written
  to disk; there is no recording archive.
- **Push-to-talk, not always-on.** No wake word in v1: capture happens only
  while the user holds the button. Always-listening changes the trust story
  entirely and stays out until explicitly wanted.
- **Action tiers.** Benign, reversible actions (start/dismiss a timer,
  add/remove one list item) are reclassified as reads and auto-run — a voice
  flow that stops to confirm every "add milk" is unusable. Destructive bulk
  actions (clear the whole list) stay confirm-gated. No shell, no filesystem,
  no arbitrary command tools — ever.
- **LAN exposure.** Binds localhost by default. If exposed to the LAN for a
  wall-tablet client, it inherits the homelab's `local-only` Traefik pattern;
  there is no auth of its own yet (single-household device).

## Decisions

- **qwen3:8b + think=False** — the spike-verified local combo: 3/3 on
  multi-step tool use at ~1-3s per turn. Spoken UX lives or dies on latency.
- **JSON-file state** — timers and a shopping list don't need a database.
- **Ringing = client concern.** The API reports `ringing: true`; making noise
  is the client's job (roadmap: a small always-on display client).
