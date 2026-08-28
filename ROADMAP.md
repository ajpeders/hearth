# hearth — roadmap

Status: **v1 backend built + live-verified** (2026-07-21, qwen3:8b): parallel
tool calls ("pasta timer + parmesan" in one turn, ~2s), sloppy-speech
interpretation, state persistence, confirm gate on destructive clear.
Tests: 4 passing (offline, fake provider).

## Next (in order)

1. **Voice client** — the actual counter UX: push-to-talk capture →
   `/api/transcribe` → chat SSE → **TTS reply** (piper or macOS `say`) +
   timer display/ring. Probably a small web page (wall tablet friendly) or a
   macOS menu-bar script to start.
2. **Timer ringing** — client polls `/api/timers` (or SSE later) and plays a
   sound on `ringing: true`.
3. **More kitchen tools** — unit conversions as a deterministic endpoint,
   simple recipes/notes store. Mealie integration is tempting but breaks the
   100%-offline rule unless Mealie runs on-device — decide later.
4. **Camera ("what am I holding?")** — vision-behind-a-tool:
   `GET /api/camera/look` captures a frame, local VLM (Ollama llava/qwen-VL)
   describes it, frame discarded. Same pattern as docuAI's search tool.
5. **Wake word** — only if push-to-talk proves annoying in practice; changes
   the trust story (see ARCHITECTURE), so it's opt-in and last.

## Non-goals

- Cloud providers, accounts, telemetry. Offline is the product.
- Multi-user/multi-room orchestration (single household device).
- Shell/file/command tools for the model.
## Make this usable by others (added 2026-08-27)

- [ ] Universalize the README / docs / code for outside users: document setup
  from scratch on generic infrastructure, replace homelab-specific assumptions
  (private hostnames, LAN addresses, personal paths and defaults) with
  env-driven configuration plus examples, and keep the public GitHub mirror
  directly runnable.
