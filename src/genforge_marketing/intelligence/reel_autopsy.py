"""Structured Reel/post autopsy from analyst observations and transcript.

This MVP reconstructs a content blueprint from supplied evidence. It does not fetch,
transcribe, inspect, or claim to watch media automatically.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class BeatObservation(BaseModel):
    timestamp_start_seconds: float = Field(ge=0)
    timestamp_end_seconds: float | None = Field(default=None, ge=0)
    visual_description: str = ""
    spoken_text: str = ""
    on_screen_text: str = ""
    action: str = ""
    inferred_role: str = "unknown"
    retention_mechanism: str = ""
    evidence_type: str = ""
    confidence: float = Field(default=0.5, ge=0, le=1)


class ReferenceInput(BaseModel):
    title: str = Field(min_length=1)
    platform: str = "unknown"
    url: str = ""
    format: str = "reel"
    objective: str = "unknown"
    metrics: dict[str, int | float | None] = Field(default_factory=dict)
    hook_observation: str = ""
    hook_text: str = ""
    beats: list[BeatObservation] = Field(default_factory=list)
    payoff_observation: str = ""
    cta_observation: str = ""
    caption: str = ""
    visual_style_notes: list[str] = Field(default_factory=list)
    editing_notes: list[str] = Field(default_factory=list)
    audio_notes: list[str] = Field(default_factory=list)
    analyst_notes: str = ""
    source_access: str = "analyst-supplied observations"


ROLE_ORDER = ["hook", "setup", "problem", "example", "process", "proof", "payoff", "cta", "other", "unknown"]


def build_autopsy(reference: ReferenceInput) -> dict[str, Any]:
    """Build an evidence-aware autopsy and original adaptation worksheet."""
    beats = sorted(reference.beats, key=lambda item: item.timestamp_start_seconds)
    observed_roles = [beat.inferred_role for beat in beats if beat.inferred_role != "unknown"]
    role_counts: dict[str, int] = {}
    for role in observed_roles:
        role_counts[role] = role_counts.get(role, 0) + 1

    text_parts = [reference.hook_text, reference.caption]
    text_parts.extend(beat.spoken_text for beat in beats)
    text_parts.extend(beat.on_screen_text for beat in beats)
    text_blob = " ".join(text_parts).lower()
    questions = text_blob.count("?")
    exclamations = text_blob.count("!")
    word_count = len(text_blob.split())

    timeline = []
    for beat in beats:
        timeline.append({
            "start_seconds": beat.timestamp_start_seconds,
            "end_seconds": beat.timestamp_end_seconds,
            "visual": beat.visual_description,
            "spoken_text": beat.spoken_text,
            "on_screen_text": beat.on_screen_text,
            "action": beat.action,
            "role": beat.inferred_role,
            "retention_mechanism": beat.retention_mechanism,
            "evidence_type": beat.evidence_type,
            "confidence": beat.confidence,
        })

    observed = {
        "hook_observation": reference.hook_observation,
        "hook_text": reference.hook_text,
        "beat_count": len(beats),
        "role_sequence": observed_roles,
        "role_counts": role_counts,
        "payoff_observation": reference.payoff_observation,
        "cta_observation": reference.cta_observation,
        "visual_style_notes": reference.visual_style_notes,
        "editing_notes": reference.editing_notes,
        "audio_notes": reference.audio_notes,
    }
    analysis = {
        "transcript_word_count": word_count,
        "question_marks_in_supplied_text": questions,
        "exclamation_marks_in_supplied_text": exclamations,
        "beat_timing_available": bool(beats),
        "role_sequence_available": bool(observed_roles),
    }
    limitations = [
        "This report is based only on supplied observations and text; it does not fetch or inspect the source media.",
        "Text counts and observed beat labels are descriptive and do not establish retention or causal performance.",
        "Metrics are source-provided and may be incomplete or incomparable across platforms.",
        "Adapt the underlying content mechanism; do not copy the creator's script, footage, distinctive design, or branding.",
    ]
    return {
        "schema_version": 1,
        "report_type": "reel_autopsy",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reference": {
            "title": reference.title,
            "platform": reference.platform,
            "url": reference.url,
            "format": reference.format,
            "objective": reference.objective,
            "metrics": reference.metrics,
            "source_access": reference.source_access,
        },
        "observations": observed,
        "timeline": timeline,
        "descriptive_analysis": analysis,
        "adaptation_worksheet": {
            "mechanism_to_adapt": "",
            "original_genforge_angle": "",
            "product_or_subject": "",
            "script_beats": [],
            "shot_list": [],
            "editing_plan": [],
            "caption_draft": "",
            "cta_draft": "",
            "quality_checks": [
                "Hook is clear before the viewer scrolls.",
                "Visual proof supports the promise.",
                "The payoff resolves the opening setup.",
                "The content uses original GenForge footage, copy, and design.",
                "Text is readable on a mobile screen.",
                "Claims are accurate and approvals are complete.",
            ],
        },
        "limitations": limitations,
    }


def load_reference(path: Any) -> ReferenceInput:
    import json
    from pathlib import Path

    return ReferenceInput.model_validate_json(Path(path).read_text(encoding="utf-8"))
