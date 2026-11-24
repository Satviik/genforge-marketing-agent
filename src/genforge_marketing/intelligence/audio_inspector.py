"""Local audio extraction and silence interval detection using FFmpeg."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from genforge_marketing.intelligence.media_inspector import MediaInspectionError

SILENCE_START = re.compile(r"silence_start: ([0-9]+(?:\.[0-9]+)?)")
SILENCE_END = re.compile(r"silence_end: ([0-9]+(?:\.[0-9]+)?)")


def extract_audio_and_detect_silence(
    input_path: Path,
    output_audio: Path,
    noise_db: float = -35.0,
    min_silence_seconds: float = 0.35,
) -> dict[str, Any]:
    """Extract mono 16kHz WAV and detect silence intervals; no transcription."""
    if noise_db > 0:
        raise ValueError("noise_db must be <= 0")
    if min_silence_seconds <= 0:
        raise ValueError("min_silence_seconds must be > 0")
    if not input_path.is_file():
        raise FileNotFoundError(input_path)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise MediaInspectionError("Audio inspection requires FFmpeg on PATH.")
    output_audio.parent.mkdir(parents=True, exist_ok=True)
    extract_cmd = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(input_path),
        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(output_audio),
    ]
    silence_cmd = [
        ffmpeg, "-hide_banner", "-loglevel", "info", "-i", str(input_path),
        "-af", f"silencedetect=noise={noise_db}dB:d={min_silence_seconds}",
        "-vn", "-f", "null", "-",
    ]
    try:
        subprocess.run(extract_cmd, capture_output=True, text=True, check=True)
        detected = subprocess.run(silence_cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr or str(exc)
        raise MediaInspectionError(f"Audio inspection failed (video may have no audio stream): {detail}") from exc

    log = detected.stderr or ""
    starts = [float(value) for value in SILENCE_START.findall(log)]
    ends = [float(value) for value in SILENCE_END.findall(log)]
    intervals = []
    for index, start in enumerate(starts):
        end = ends[index] if index < len(ends) else None
        intervals.append({"start_seconds": start, "end_seconds": end,
                         "duration_seconds": round(end - start, 3) if end is not None else None})
    return {
        "schema_version": 1,
        "inspection_type": "audio_extract_silence",
        "source_file": input_path.name,
        "audio_file": str(output_audio),
        "audio_format": {"sample_rate_hz": 16000, "channels": 1, "encoding": "pcm_s16le"},
        "silence_detection": {"noise_threshold_db": noise_db, "minimum_duration_seconds": min_silence_seconds,
                              "interval_count": len(intervals), "intervals": intervals},
        "limitations": [
            "Silence detection is a threshold-based heuristic.",
            "Audio is extracted but speech is not transcribed or semantically analyzed.",
            "Audio files may contain copyrighted music or speech; ensure you have permission to analyze and retain them.",
        ],
    }
