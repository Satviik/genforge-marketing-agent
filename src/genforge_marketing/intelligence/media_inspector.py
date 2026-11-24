"""Local media inspection and frame sampling using FFmpeg tools.

This module indexes media metadata and extracts evenly spaced still frames. It does
not perform visual interpretation, transcription, or claim to understand frames.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


class MediaInspectionError(RuntimeError):
    """Raised when FFprobe/FFmpeg is missing or media processing fails."""


def inspect_media(input_path: Path, frames_dir: Path, interval_seconds: float = 2.0) -> dict[str, Any]:
    """Read video metadata and sample frames locally at a fixed interval."""
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be greater than zero")
    if not input_path.is_file():
        raise FileNotFoundError(input_path)
    ffprobe = shutil.which("ffprobe")
    ffmpeg = shutil.which("ffmpeg")
    if not ffprobe or not ffmpeg:
        raise MediaInspectionError("Media inspection requires FFmpeg and FFprobe on PATH.")

    try:
        probe = subprocess.run(
            [ffprobe, "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=width,height,r_frame_rate,codec_name:format=duration", "-of", "json",
             str(input_path)],
            capture_output=True, text=True, check=True,
        )
        metadata = json.loads(probe.stdout)
        stream = metadata.get("streams", [{}])[0]
        duration = float(metadata.get("format", {}).get("duration", 0))
        frames_dir.mkdir(parents=True, exist_ok=True)
        pattern = frames_dir / "frame_%04d.jpg"
        subprocess.run(
            [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(input_path),
             "-vf", f"fps=1/{interval_seconds}", "-q:v", "2", str(pattern)],
            capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, json.JSONDecodeError, IndexError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        raise MediaInspectionError(f"Media inspection failed: {detail}") from exc

    frame_files = sorted(frames_dir.glob("frame_*.jpg"))
    return {
        "schema_version": 1,
        "inspection_type": "local_video_frame_index",
        "source_file": input_path.name,
        "metadata": {
            "duration_seconds": duration,
            "width": stream.get("width"),
            "height": stream.get("height"),
            "frame_rate": stream.get("r_frame_rate"),
            "video_codec": stream.get("codec_name"),
        },
        "sampling": {
            "interval_seconds": interval_seconds,
            "frame_count": len(frame_files),
            "frames": [
                {"index": index, "approx_timestamp_seconds": round(index * interval_seconds, 3),
                 "file": str(frame.relative_to(frames_dir.parent))}
                for index, frame in enumerate(frame_files)
            ],
        },
        "limitations": [
            "Frames are sampled mechanically; no visual interpretation is performed.",
            "Sampling timestamps are approximate and may not align with scene changes.",
            "Audio is not extracted or transcribed by this command.",
        ],
    }
