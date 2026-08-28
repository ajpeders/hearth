"""Local speech-to-text via faster-whisper. Optional dep (hearth[voice]) —
the API runs without it, /api/transcribe just returns 501.

Model runs entirely on-device; audio never leaves the machine and is not
stored — bytes in, text out, discarded.
"""
import os
import tempfile

_model = None


def available() -> bool:
    try:
        import faster_whisper  # noqa: F401
        return True
    except ImportError:
        return False


def transcribe(audio: bytes, suffix: str = ".wav") -> str:
    global _model
    from faster_whisper import WhisperModel

    if _model is None:
        # small = good accuracy/speed balance on Apple Silicon / modern CPUs
        _model = WhisperModel(
            os.environ.get("HEARTH_WHISPER_MODEL", "small"),
            compute_type="int8",
        )
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as f:
        f.write(audio)
        f.flush()
        segments, _info = _model.transcribe(f.name, vad_filter=True)
        return " ".join(s.text.strip() for s in segments).strip()
