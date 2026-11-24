"""Optional local speech transcription using faster-whisper."""
from __future__ import annotations

from pathlib import Path
from typing import Any


class TranscriptionError(RuntimeError):
    """Raised when optional local transcription cannot run."""


def transcribe_audio(
    audio_file: Path,
    model_size: str = "base",
    device: str = "cpu",
    compute_type: str = "int8",
    language: str | None = None,
) -> dict[str, Any]:
    """Transcribe audio with a locally running faster-whisper model."""
    if not audio_file.is_file():
        raise FileNotFoundError(audio_file)
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise TranscriptionError(
            "Transcription is optional. Install it with: pip install genforge-marketing-agent[transcription]"
        ) from exc

    try:
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        segments, info = model.transcribe(str(audio_file), language=language, vad_filter=True)
        transcript_segments = [
            {
                "start_seconds": round(float(segment.start), 3),
                "end_seconds": round(float(segment.end), 3),
                "text": segment.text.strip(),
            }
            for segment in segments
        ]
    except Exception as exc:
        raise TranscriptionError(f"Local transcription failed: {exc}") from exc

    return {
        "schema_version": 1,
        "analysis_type": "local_speech_transcription",
        "source_audio": audio_file.name,
        "model": model_size,
        "device": device,
        "language": getattr(info, "language", language),
        "language_probability": getattr(info, "language_probability", None),
        "segments": transcript_segments,
        "transcript": " ".join(item["text"] for item in transcript_segments),
        "limitations": [
            "Speech recognition can mishear names, technical terms, slang, and multilingual speech.",
            "This is a transcript, not an interpretation of creative intent or emotional tone.",
            "The model runs locally after its model weights are downloaded; no paid API is used.",
        ],
    }
