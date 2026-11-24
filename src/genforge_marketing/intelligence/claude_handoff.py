"""Export creative research and brief into a Claude-ready Markdown handoff."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def render_claude_package(
    brief: dict[str, Any],
    creative_breakdown: dict[str, Any] | None = None,
    timeline: dict[str, Any] | None = None,
    visual_notes: dict[str, Any] | None = None,
) -> str:
    """Render a self-contained, reviewable prompt package without calling Claude."""
    product = brief.get("product", {})
    campaign = brief.get("campaign", {})
    concept = brief.get("creative_concept", {})
    production = brief.get("production_plan", {})
    adaptation = brief.get("reference_adaptation", {})
    def block(title: str, value: Any) -> str:
        return "## " + title + "\n\n" + json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    sections = [
        "# GenForge Creative Production Handoff",
        "**Status:** Draft — requires human review",
        "",
        "## Task for Claude",
        "Act as a short-form creative director, scriptwriter, and production planner. Use the research below to develop a polished, ORIGINAL Reel concept and production-ready script for GenForge. Do not copy reference wording, shots, distinctive compositions, products, or creator identity. Treat observations as evidence or hypotheses, not proven causal rules. Make assumptions explicit and avoid unsupported product claims.",
        "",
        "## Product & Campaign",
        f"- Product: {product.get('name', 'unspecified')}",
        f"- Description: {product.get('description', '')}",
        f"- Objective: {campaign.get('objective', 'awareness')}",
        f"- Audience: {campaign.get('audience', '')}",
        f"- Platform: {campaign.get('platform', 'Instagram Reels')}",
        f"- Target runtime: {campaign.get('duration_seconds', 20)} seconds",
        f"- Brand voice: {campaign.get('brand_voice', '')}",
        "",
        "## Creative Concept & Hooks",
        concept.get("title", ""),
        concept.get("core_idea", ""),
        "",
        *[f"- {h}" for h in concept.get("hook_options", [])],
        "",
        "## Draft Production Plan",
        *[f"- {scene.get('start_seconds')}–{scene.get('end_seconds')}s — **{scene.get('phase')}**: {scene.get('visual_direction')} | Script/text: {scene.get('voiceover_or_text')} | Edit: {scene.get('editing_notes')}" for scene in production.get("scenes", [])],
        "",
        "## Shot List",
        *[f"- {shot}" for shot in production.get("shot_list", [])],
        "",
        "## Direction",
        f"- Visual direction: {production.get('visual_direction', '')}",
        f"- Audio: {production.get('audio_direction', '')}",
        f"- Caption draft: {production.get('caption_draft', '')}",
        *[f"- CTA: {cta}" for cta in production.get("cta_options", [])],
        *[f"- Hashtag: {tag}" for tag in production.get("hashtags", [])],
        "",
        "## Reference Adaptation Notes",
        "Reuse abstract mechanics only; create fresh content.",
        *[f"- {principle}" for principle in adaptation.get("adapted_mechanics", [])],
        *[f"- Source observation: {principle}" for principle in adaptation.get("source_principles", [])],
        *[f"- Guardrail: {rule}" for rule in concept.get("originality_guardrails", [])],
        "",
    ]
    if creative_breakdown:
        sections.extend([block("Creative Breakdown Evidence", creative_breakdown), ""])
    if timeline:
        sections.extend([block("Reconstructed Timeline Evidence", timeline), ""])
    if visual_notes:
        sections.extend([block("Manual Frame Notes", visual_notes), ""])
    sections.extend([
        "## Deliverables Requested from Claude",
        "1. Improve the concept and select the strongest hook, explaining the choice briefly.",
        "2. Write a timestamped script with shot, camera/action, narration, on-screen text, sound, transition and purpose per beat.",
        "3. Give a practical filming/Blender/3D-printing shot checklist and a minimal edit plan.",
        "4. Provide a caption and one CTA, with optional A/B hook alternatives.",
        "5. Preserve the target runtime and budget-conscious production constraints; prioritize footage GenForge can capture itself.",
        "6. Keep the result original, truthful, product-specific, and ready for human review.",
        "",
        "## Human Review Gate",
        "Verify product facts, copyright/licensing, audio rights, feasibility, CTA, and the final edit. This package does not publish content.",
    ])
    return "\n".join(sections).strip() + "\n"


def export_claude_package(
    brief_path: str | Path,
    output_path: str | Path,
    breakdown_path: str | Path | None = None,
    timeline_path: str | Path | None = None,
    visual_notes_path: str | Path | None = None,
) -> Path:
    def load(path: str | Path | None) -> dict[str, Any]:
        return json.loads(Path(path).read_text(encoding="utf-8")) if path else {}
    brief = load(brief_path)
    if brief.get("artifact_type") != "original_reel_creative_brief":
        raise ValueError("Input brief is not an original Reel creative brief")
    result = render_claude_package(brief, load(breakdown_path), load(timeline_path), load(visual_notes_path))
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(result, encoding="utf-8")
    return destination
