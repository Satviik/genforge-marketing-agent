"""Produce a reusable creative-structure breakdown from evidence reports."""
from __future__ import annotations
from typing import Any


def build_creative_breakdown(timeline: dict[str, Any] | None = None,
                            visual_notes: dict[str, Any] | None = None) -> dict[str, Any]:
    timeline = timeline or {}
    visual_notes = visual_notes or {}
    events = timeline.get("timeline", [])
    frames = visual_notes.get("frames", [])
    frame_map = {str(f.get("timestamp_seconds")): f for f in frames}
    phases = []
    for event in events:
        kind = event.get("event_type", "event")
        ts = float(event.get("timestamp_seconds", 0))
        if kind == "scene_change":
            role = "visual_reset"
        elif kind == "possible_hook":
            role = "hook_candidate"
        elif kind == "possible_payoff":
            role = "payoff_candidate"
        elif kind == "explanation_or_process":
            role = "process_or_explanation"
        elif kind == "silence":
            role = "pause_or_audio_gap"
        elif kind == "sampled_frame":
            role = "visual_evidence"
        else:
            role = "supporting_event"
        phase = {"timestamp_seconds": ts, "role": role, "event_type": kind,
                 "evidence": event.get("evidence", ""), "interpretation": event.get("interpretation", "")}
        # Match frame observations using a small tolerance to account for float formatting.
        nearest = next((f for f in frames if abs(float(f.get("timestamp_seconds", 0))-ts) <= 0.15), None)
        if nearest:
            phase["visual_observations"] = nearest.get("observations", {})
        phases.append(phase)
    phases.sort(key=lambda p: p["timestamp_seconds"])
    roles = [p["role"] for p in phases]
    formula = []
    if "hook_candidate" in roles: formula.append("Hook candidate")
    if "visual_reset" in roles: formula.append("Visual reset(s)")
    if "process_or_explanation" in roles: formula.append("Process / explanation")
    if "pause_or_audio_gap" in roles: formula.append("Pause or audio gap")
    if "payoff_candidate" in roles: formula.append("Payoff candidate")
    formula.append("CTA: not detectable from current evidence; annotate manually")
    return {
        "schema_version": 1, "analysis_type": "creative_structure_breakdown",
        "source_file": timeline.get("source_file") or visual_notes.get("source_file"),
        "phases": phases, "observed_structure": formula,
        "adaptation_guidance": [
            "Reuse the sequence mechanics, not the source's wording, product, or distinctive visuals.",
            "Replace the subject with a GenForge product and create original shots and copy.",
            "Add a clear product benefit or proof moment; current evidence may not establish one.",
            "Design a CTA for the intended goal; CTA is not inferred by this tool.",
        ],
        "confidence": "low" if not visual_notes else "medium (manual visual notes are present; completeness is not assessed)",
        "limitations": ["Roles are heuristics derived from event labels and transcript cues.",
                       "Visual observations are only as reliable as manually entered notes.",
                       "This does not measure retention, causality, or audience performance."],
    }
