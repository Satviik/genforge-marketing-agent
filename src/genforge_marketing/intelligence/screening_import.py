"""Import adapter for Screening Agent JSON export schema v1."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .radar import TrendSignal


def import_screening_export(path: Path) -> list[TrendSignal]:
    """Validate Screening Agent v1 export and map items into TrendSignal.

    The source export is produced by gen-forge-screening-agent's `export` command.
    Fields not present in that export (e.g. saves/follower counts) remain unknown.
    """
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Screening export must be a JSON object.")
    if payload.get("schema_version") != 1:
        raise ValueError("Unsupported Screening export schema_version; expected 1.")
    if payload.get("source_agent") != "gen-forge-screening-agent":
        raise ValueError("Unexpected source_agent in Screening export.")
    items = payload.get("items")
    if not isinstance(items, list):
        raise ValueError("Screening export 'items' must be a list.")

    signals: list[TrendSignal] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"Screening export item {index} must be an object.")
        raw = item.get("raw") if isinstance(item.get("raw"), dict) else {}
        signals.append(
            TrendSignal(
                title=str(item.get("topic") or "Untitled social content"),
                platform=str(item.get("source") or "unknown"),
                url=item.get("source_url"),
                creator=raw.get("creator"),
                published_at=item.get("raw", {}).get("published_at") if isinstance(item.get("raw"), dict) else None,
                collected_at=item.get("observed_at"),
                views=item.get("views"),
                likes=item.get("likes"),
                comments=item.get("comments"),
                shares=item.get("raw", {}).get("shares") if isinstance(item.get("raw"), dict) else None,
                category=str(raw.get("search_term") or "general"),
                notes=str(item.get("summary") or ""),
                data_completeness=_completeness(item),
            )
        )
    return signals


def _completeness(item: dict[str, Any]) -> float:
    """Simple availability ratio for exported metrics/source metadata."""
    fields = ("source", "source_url", "observed_at", "views", "likes", "comments")
    present = sum(item.get(field) not in (None, "") for field in fields)
    return round(present / len(fields), 4)
