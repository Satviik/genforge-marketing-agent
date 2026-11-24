"""FFmpeg scene-change detection for local videos."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from genforge_marketing.intelligence.media_inspector import MediaInspectionError

PTS_RE = re.compile(r"pts_time:([0-9]+(?:\.[0-9]+)?)")
SCORE_RE = re.compile(r"lavfi\.scene_score:([0-9]+(?:\.[0-9]+)?)")


def detect_scene_changes(input_path: Path, threshold: float = 0.30) -> dict[str, Any]:
    """Detect visual scene changes with FFmpeg's scene-change filter.

    The threshold is a heuristic from 0 to 1. This detects visual differences,
    not semantic scenes or storytelling beats.
    """
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    if not input_path.is_file():
        raise FileNotFoundError(input_path)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise MediaInspectionError("Scene detection requires FFmpeg on PATH.")
    command = [
        ffmpeg, "-hide_banner", "-loglevel", "info", "-i", str(input_path),
        "-vf", f"select='gt(scene,{threshold})',showinfo",
        "-an", "-f", "null", "-",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as exc:
        raise MediaInspectionError(f"Scene detection failed: {exc.stderr or exc}") from exc

    timestamps = PTS_RE.findall(result.stderr)
    scores = SCORE_RE.findall(result.stderr)
    changes = [
        {"index": index + 1, "timestamp_seconds": float(ts),
         "scene_score": float(scores[index]) if index < len(scores) else None}
        for index, ts in enumerate(timestamps)
    ]
    return {
        "schema_version": 1,
        "inspection_type": "scene_change_detection",
        "source_file": input_path.name,
        "threshold": threshold,
        "scene_change_count": len(changes),
        "scene_changes": changes,
        "limitations": [
            "Scene changes are detected from pixel-level visual differences, not semantic meaning.",
            "Rapid motion, flashes, or camera movement can trigger false positives.",
            "Threshold selection affects results and should be tuned for the source.",
        ],
    }
