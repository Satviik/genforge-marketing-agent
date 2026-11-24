"""Trend Radar and creative reference intelligence.

This first version is provider-neutral and deterministic. It accepts fixture JSON,
manual references, stores them in SQLite, scores available signals, and extracts
Creative DNA from supplied analysis notes (not from unseen video).
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl


class TrendSignal(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    platform: str = "unknown"
    url: HttpUrl | None = None
    creator: str | None = None
    published_at: datetime | None = None
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    views: int | None = Field(default=None, ge=0)
    likes: int | None = Field(default=None, ge=0)
    comments: int | None = Field(default=None, ge=0)
    shares: int | None = Field(default=None, ge=0)
    saves: int | None = Field(default=None, ge=0)
    creator_followers: int | None = Field(default=None, ge=0)
    duration_seconds: float | None = Field(default=None, ge=0)
    category: str = "general"
    notes: str = ""
    data_completeness: float = Field(default=0.0, ge=0, le=1)


class CreativeDNA(BaseModel):
    """Structured content blueprint for dissecting high-performing posts and Reels.

    Fields are observations supplied by an analyst or a future media-analysis adapter;
    the schema itself does not claim to inspect source media.
    """
    content_format: str = "unknown"
    objective: str = "unknown"
    hook_type: str = "unknown"
    opening_mechanism: str = ""
    opening_frame: str = ""
    hook_text: str = ""
    story_structure: list[str] = Field(default_factory=list)
    beat_map: list[str] = Field(default_factory=list)
    retention_devices: list[str] = Field(default_factory=list)
    proof_type: str = ""
    payoff_type: str = ""
    cta_type: str = ""
    cta_text: str = ""
    caption_structure: list[str] = Field(default_factory=list)
    carousel_slide_structure: list[str] = Field(default_factory=list)
    visual_hierarchy: list[str] = Field(default_factory=list)
    visual_patterns: list[str] = Field(default_factory=list)
    editing_patterns: list[str] = Field(default_factory=list)
    audio_patterns: list[str] = Field(default_factory=list)
    psychological_triggers: list[str] = Field(default_factory=list)
    comment_prompt: str = ""
    adaptable_principles: list[str] = Field(default_factory=list)
    replication_notes: str = ""
    analysis_notes: str = ""
    confidence: float = Field(default=0.0, ge=0, le=1)


class Reference(BaseModel):
    id: str = ""
    signal: TrendSignal
    dna: CreativeDNA = Field(default_factory=CreativeDNA)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def score_signal(signal: TrendSignal) -> dict[str, Any]:
    """Transparent weighted score; missing fields are excluded and weights renormalized."""
    components: dict[str, float] = {}
    weights = {"engagement": 0.35, "relative_reach": 0.25, "recency": 0.20, "completeness": 0.20}
    if signal.views and signal.views > 0:
        rate = ((signal.likes or 0) + (signal.comments or 0) + (signal.shares or 0) + (signal.saves or 0)) / signal.views
        components["engagement"] = min(rate / 0.12, 1.0)
    if signal.views is not None and signal.creator_followers and signal.creator_followers > 0:
        components["relative_reach"] = min(signal.views / signal.creator_followers / 10, 1.0)
    if signal.published_at:
        age_days = max((signal.collected_at - signal.published_at).total_seconds() / 86400, 0)
        components["recency"] = max(0.0, 1.0 - age_days / 60)
    components["completeness"] = signal.data_completeness
    used = sum(weights[k] for k in components)
    score = sum(components[k] * weights[k] for k in components) / used if used else 0.0
    return {"score": round(score, 4), "components": {k: round(v, 4) for k, v in components.items()}, "confidence": round(used, 4)}


def extract_dna(notes: dict[str, Any]) -> CreativeDNA:
    """Validate human/AI-supplied analysis notes; does not claim to watch media."""
    return CreativeDNA.model_validate(notes)


class ReferenceStore:
    def __init__(self, path: Path = Path("data/radar.sqlite")) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS references_store
                (id TEXT PRIMARY KEY, category TEXT, score REAL, data TEXT, created_at TEXT)""")

    def add(self, reference: Reference) -> str:
        if not reference.id:
            reference.id = f"ref-{uuid4().hex[:12]}"
        score = score_signal(reference.signal)["score"]
        payload = reference.model_dump(mode="json")
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT OR REPLACE INTO references_store VALUES (?, ?, ?, ?, ?)",
                (reference.id, reference.signal.category, score, json.dumps(payload), reference.created_at.isoformat()))
        return reference.id

    def list(self, category: str | None = None) -> list[dict[str, Any]]:
        with sqlite3.connect(self.path) as db:
            query = "SELECT id, category, score, data FROM references_store"
            args: tuple[Any, ...] = ()
            if category:
                query += " WHERE category=?"
                args = (category,)
            query += " ORDER BY score DESC, created_at DESC"
            rows = db.execute(query, args).fetchall()
        return [{"id": r[0], "category": r[1], "score": r[2], "reference": json.loads(r[3])} for r in rows]

    def get(self, reference_id: str) -> dict[str, Any] | None:
        with sqlite3.connect(self.path) as db:
            row = db.execute("SELECT data FROM references_store WHERE id=?", (reference_id,)).fetchone()
        return json.loads(row[0]) if row else None


def load_fixture(path: Path) -> list[TrendSignal]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [TrendSignal.model_validate(item) for item in data]


def build_report(signals: list[TrendSignal]) -> dict[str, Any]:
    ranked = sorted(
        [{"signal": s.model_dump(mode="json"), **score_signal(s)} for s in signals],
        key=lambda x: x["score"], reverse=True,
    )
    patterns: dict[str, int] = {}
    for signal in signals:
        for tag in signal.notes.lower().split(","):
            tag = tag.strip()
            if tag:
                patterns[tag] = patterns.get(tag, 0) + 1
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(ranked),
        "ranked_signals": ranked,
        "recurring_note_patterns": sorted(patterns.items(), key=lambda item: item[1], reverse=True),
        "limitations": ["Fixture/manual signals only unless a live provider is configured.", "Single snapshots do not establish trend velocity.", "Scores are transparent heuristics, not performance predictions."],
    }


def summarize_creative_patterns(references: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate recurring Creative DNA patterns from stored reference records."""
    from collections import Counter

    fields = {
        "content_formats": "content_format",
        "objectives": "objective",
        "hook_types": "hook_type",
        "payoff_types": "payoff_type",
        "cta_types": "cta_type",
        "proof_types": "proof_type",
        "retention_devices": "retention_devices",
        "caption_structures": "caption_structure",
        "carousel_slide_structures": "carousel_slide_structure",
        "visual_hierarchy": "visual_hierarchy",
        "visual_patterns": "visual_patterns",
        "editing_patterns": "editing_patterns",
        "audio_patterns": "audio_patterns",
        "psychological_triggers": "psychological_triggers",
        "adaptable_principles": "adaptable_principles",
    }
    counters = {key: Counter() for key in fields}
    for row in references:
        ref = row.get("reference", row)
        dna = ref.get("dna", {}) if isinstance(ref, dict) else {}
        for key, field_name in fields.items():
            value = dna.get(field_name)
            if isinstance(value, str):
                values = [value]
            elif isinstance(value, list):
                values = value
            else:
                values = []
            for item in values:
                if not isinstance(item, str):
                    continue
                normalized = item.strip()
                if not normalized or normalized.casefold() == "unknown":
                    continue
                counters[key][normalized] += 1
    return {
        "reference_count": len(references),
        "patterns": {
            key: [{"pattern": pattern, "count": count} for pattern, count in counter.most_common()]
            for key, counter in counters.items()
        },
        "note": "Frequency counts summarize supplied Creative DNA notes; they are not evidence of causality or guaranteed performance.",
    }
