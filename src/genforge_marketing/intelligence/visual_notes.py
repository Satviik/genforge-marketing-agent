"""Create editable frame-by-frame visual observation templates."""
from __future__ import annotations
from typing import Any


OBSERVATION_FIELDS = {
    "shot_type": "",
    "subject": "",
    "framing": "",
    "camera_angle": "",
    "camera_movement": "",
    "subject_action": "",
    "background_environment": "",
    "lighting": "",
    "dominant_colors": [],
    "text_overlay": "",
    "composition_notes": "",
    "transition_or_cut": "",
    "creative_purpose_guess": "",
    "confidence": "low",
}


def build_visual_notes_template(media_report: dict[str, Any]) -> dict[str, Any]:
    frames = media_report.get("sampling", {}).get("frames", [])
    notes = []
    for index, frame in enumerate(frames):
        notes.append({
            "frame_index": index,
            "timestamp_seconds": frame.get("approx_timestamp_seconds", 0),
            "image_file": frame.get("file", ""),
            "observations": dict(OBSERVATION_FIELDS),
        })
    return {
        "schema_version": 1,
        "analysis_type": "frame_visual_notes",
        "source_file": media_report.get("source_file"),
        "instructions": "Fill observations from the frame image. Keep observed facts separate from creative-purpose guesses.",
        "observation_fields": list(OBSERVATION_FIELDS),
        "frames": notes,
        "limitations": ["This is an annotation template; no visual model has inspected these images.",
                       "Creative purpose is an analyst hypothesis, not verified audience behavior."],
    }


def validate_visual_notes(notes: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    frames = notes.get("frames")
    if not isinstance(frames, list):
        return ["frames must be a list"]
    seen = set()
    for index, frame in enumerate(frames):
        if not isinstance(frame, dict):
            errors.append(f"frames[{index}] must be an object")
            continue
        ts = frame.get("timestamp_seconds")
        if ts is not None:
            try:
                if float(ts) < 0:
                    errors.append(f"frames[{index}] timestamp_seconds cannot be negative")
            except (TypeError, ValueError):
                errors.append(f"frames[{index}] timestamp_seconds must be numeric")
        fid = frame.get("frame_index")
        if fid in seen:
            errors.append(f"duplicate frame_index: {fid}")
        seen.add(fid)
        if not isinstance(frame.get("observations"), dict):
            errors.append(f"frames[{index}].observations must be an object")
    return errors
