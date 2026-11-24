"""Generate original, evidence-informed Reel briefs from reusable creative mechanics."""
from __future__ import annotations

from typing import Any


def generate_original_reel(
    product_name: str,
    product_description: str = "",
    objective: str = "awareness",
    audience: str = "people interested in custom 3D printed products",
    platform: str = "Instagram Reels",
    duration_seconds: int = 20,
    brand_voice: str = "creative, helpful, maker-focused",
    creative_breakdown: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a deterministic draft brief; no model/API is called."""
    if not product_name.strip():
        raise ValueError("product_name must not be blank")
    if not 8 <= duration_seconds <= 90:
        raise ValueError("duration_seconds must be between 8 and 90")
    breakdown = creative_breakdown or {}
    phases = breakdown.get("phases", [])
    roles = [str(item.get("role", "")) for item in phases]
    principles = breakdown.get("adaptation_guidance", [])
    # Scale a six-beat structure to the requested runtime.
    weights = [0.10, 0.12, 0.18, 0.25, 0.23, 0.12]
    labels = [
        ("Hook", "Show the finished product or its most surprising detail immediately."),
        ("Problem/context", "Reveal the everyday problem or the customization opportunity."),
        ("Design", "Show the product design or personalization choices taking shape."),
        ("Process", "Show tactile making moments: print layers, finishing, assembly or details."),
        ("Payoff", "Reveal the finished product in a clean, satisfying hero shot; demonstrate its benefit."),
        ("CTA", "Invite a specific comment, customization request or DM aligned with the campaign goal."),
    ]
    # Allocate integer scene lengths using largest remainder, with at least 1s per beat.
    raw_lengths = [duration_seconds * weight for weight in weights]
    lengths = [max(1, int(value)) for value in raw_lengths]
    while sum(lengths) > duration_seconds:
        candidates = [i for i, value in enumerate(lengths) if value > 1]
        if not candidates:
            break
        index = min(candidates, key=lambda i: raw_lengths[i] - int(raw_lengths[i]))
        lengths[index] -= 1
    while sum(lengths) < duration_seconds:
        index = max(range(len(lengths)), key=lambda i: raw_lengths[i] - lengths[i])
        lengths[index] += 1
    scenes = []
    cursor = 0
    for idx, (label, direction) in enumerate(labels):
        start = cursor
        end = start + lengths[idx]
        cursor = end
        scenes.append({
            "scene": idx + 1, "phase": label, "start_seconds": start, "end_seconds": end,
            "duration_seconds": end - start, "visual_direction": direction,
            "voiceover_or_text": (
                f"Show {product_name} clearly." if idx == 0 else
                f"Highlight how {product_name} solves or personalizes the problem." if idx == 1 else
                "Keep the explanation short; let visuals carry the process." if idx in (2, 3) else
                f"Make the benefit of {product_name} unmistakable." if idx == 4 else
                "Use one simple CTA; avoid multiple asks."
            ),
            "editing_notes": (
                "Open on motion or a strong close-up; text should be short and readable."
                if idx == 0 else
                "Use quick cuts or a match cut to keep forward momentum."
                if idx in (1, 2, 3) else
                "Slow down slightly for the reveal; use clean lighting and detail shots."
                if idx == 4 else "Hold the final frame long enough to read the CTA."
            ),
        })
    return {
        "schema_version": 1,
        "artifact_type": "original_reel_creative_brief",
        "status": "draft_for_review",
        "provider": "deterministic_local_template",
        "model_used": None,
        "product": {"name": product_name.strip(), "description": product_description},
        "campaign": {"objective": objective, "audience": audience, "platform": platform,
                     "duration_seconds": duration_seconds, "brand_voice": brand_voice},
        "creative_concept": {
            "title": f"{product_name.strip()} — transformation reveal",
            "core_idea": f"Make {product_name.strip()} the visual payoff; tell the story through the design-to-finished-product transformation.",
            "hook_options": [
                f"Show the finished {product_name.strip()} before viewers know how it was made.",
                "Open with the most satisfying detail or unexpected use of {product_name.strip()}.",
                f"Ask: 'What if this could be made just for you?' then reveal {product_name.strip()}."
            ],
            "originality_guardrails": [
                "Use only the reference's broad structure mechanics, not its wording, footage, product, or distinctive composition.",
                "Create original shots, narration and on-screen text for this product.",
                "Treat reference interpretations as hypotheses, not proven causes of performance."
            ],
        },
        "production_plan": {"scenes": scenes, "shot_list": [
            "Hero macro/detail shot", "Problem or customization context", "CAD/model screen capture",
            "Printer in motion", "Finishing/assembly detail", "Final product in-use reveal"
        ], "audio_direction": "Use licensed or original audio; align cuts to natural beats where practical.",
            "visual_direction": "Maker-focused, tactile close-ups, clear lighting, intentional camera movement, product-first framing.",
            "caption_draft": f"Made to match your idea—not mass produced. What would you customize?\n\n{product_name.strip()} by GenForge.",
            "cta_options": ["Comment your customization idea", "DM GenForge for a custom order"],
            "hashtags": ["#3DPrinting", "#CustomMade", "#GenForge", "#MadeForYou"]},
        "reference_adaptation": {
            "source_structure_roles": roles,
            "source_principles": principles,
            "adapted_mechanics": ["front-load the visual payoff", "build curiosity with process progression", "deliver a clear proof/reveal", "end with one goal-aligned CTA"],
            "note": "Reference mechanics are summarized only; this brief does not reproduce source creative.",
        },
        "limitations": [
            "This is a deterministic starter brief, not generative AI output.",
            "Validate product claims, footage availability, duration and CTA before production.",
            "Reference structure may be incomplete or heuristic if upstream annotations are incomplete.",
        ],
    }
