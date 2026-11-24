"""One-step offline campaign package assembly for brief + Claude handoff."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from genforge_marketing.intelligence.creative_generator import generate_original_reel
from genforge_marketing.intelligence.claude_handoff import render_claude_package


def build_campaign_pack(
    product_name: str,
    product_description: str = "",
    objective: str = "awareness",
    audience: str = "people interested in custom 3D printed products",
    platform: str = "Instagram Reels",
    duration_seconds: int = 20,
    brand_voice: str = "creative, helpful, maker-focused",
    creative_breakdown: dict[str, Any] | None = None,
    timeline: dict[str, Any] | None = None,
    visual_notes: dict[str, Any] | None = None,
) -> dict[str, Any]:
    brief = generate_original_reel(product_name, product_description, objective, audience, platform, duration_seconds, brand_voice, creative_breakdown)
    handoff = render_claude_package(brief, creative_breakdown, timeline, visual_notes)
    return {"creative_brief": brief, "claude_handoff_markdown": handoff, "status": "draft_for_review", "external_model_called": False}


def write_campaign_pack(pack: dict[str, Any], brief_path: str | Path, handoff_path: str | Path) -> tuple[Path, Path]:
    brief_destination, handoff_destination = Path(brief_path), Path(handoff_path)
    brief_destination.parent.mkdir(parents=True, exist_ok=True)
    handoff_destination.parent.mkdir(parents=True, exist_ok=True)
    brief_destination.write_text(json.dumps(pack["creative_brief"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    handoff_destination.write_text(pack["claude_handoff_markdown"], encoding="utf-8")
    return brief_destination, handoff_destination
