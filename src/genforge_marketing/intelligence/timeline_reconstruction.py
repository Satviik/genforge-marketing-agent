"""Evidence-based timeline reconstruction from local media analysis outputs."""
from __future__ import annotations
from typing import Any


def reconstruct_timeline(media: dict[str, Any] | None = None, scenes: dict[str, Any] | None = None,
                       audio: dict[str, Any] | None = None, transcript: dict[str, Any] | None = None) -> dict[str, Any]:
    """Merge extracted evidence into a timeline; labels remain heuristic, not semantic AI."""
    media = media or {}
    scenes = scenes or {}
    audio = audio or {}
    transcript = transcript or {}
    events: list[dict[str, Any]] = []
    for frame in media.get("sampling", {}).get("frames", []):
        events.append({"timestamp_seconds": float(frame.get("approx_timestamp_seconds", 0)),
                     "event_type": "sampled_frame", "evidence": frame.get("file", ""),
                     "interpretation": "sampled frame; visual meaning not analyzed"})
    for cut in scenes.get("scene_changes", []):
        events.append({"timestamp_seconds": float(cut.get("timestamp_seconds", 0)),
                     "event_type": "scene_change", "evidence": cut.get("scene_score"),
                     "interpretation": "visual change candidate"})
    for silence in audio.get("silence_detection", {}).get("intervals", []):
        start = silence.get("start_seconds")
        end = silence.get("end_seconds")
        events.append({"timestamp_seconds": float(start or 0), "end_seconds": end,
                     "event_type": "silence", "evidence": silence.get("duration_seconds"),
                     "interpretation": "threshold-detected silence"})
    segments = transcript.get("segments", [])
    for segment in segments:
        text = str(segment.get("text", "")).strip()
        words = text.split()
        label = "spoken_segment"
        # Transparent text heuristics only; no claims about viewer retention.
        if segment.get("start_seconds", 0) <= 3 and ("?" in text or any(word.lower() in {"stop", "wait", "look", "why", "how"} for word in words[:4])):
            label = "possible_hook"
        elif any(word.lower().strip(".,!?") in {"because", "here's", "first", "step", "before", "after"} for word in words):
            label = "explanation_or_process"
        elif any(word.lower().strip(".,!?") in {"finally", "result", "finished", "look", "revealed"} for word in words):
            label = "possible_payoff"
        events.append({"timestamp_seconds": float(segment.get("start_seconds", 0)),
                     "end_seconds": segment.get("end_seconds"), "event_type": label,
                     "evidence": text, "interpretation": "transcript text heuristic; verify manually"})
    events.sort(key=lambda item: item["timestamp_seconds"])
    duration = media.get("metadata", {}).get("duration_seconds")
    return {
        "schema_version": 1, "analysis_type": "reel_timeline_reconstruction",
        "source_file": media.get("source_file") or scenes.get("source_file") or audio.get("source_file"),
        "duration_seconds": duration, "event_count": len(events), "timeline": events,
        "evidence_summary": {"sampled_frames": sum(e["event_type"] == "sampled_frame" for e in events),
                            "scene_changes": sum(e["event_type"] == "scene_change" for e in events),
                            "silence_intervals": sum(e["event_type"] == "silence" for e in events),
                            "transcript_segments": sum(e["event_type"] in {"spoken_segment","possible_hook","explanation_or_process","possible_payoff"} for e in events)},
        "limitations": ["Events are merged from supplied JSON reports; missing sources are allowed.",
                        "Text labels are transparent heuristics, not AI semantic analysis.",
                        "Scene-change and silence detectors can produce false positives/negatives.",
                        "Frame images are indexed but not visually understood; manual verification is required."]
    }
