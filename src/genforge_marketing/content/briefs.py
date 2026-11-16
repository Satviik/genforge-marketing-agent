"""Content brief construction."""

from pydantic import BaseModel, Field

from genforge_marketing.models.opportunity import TrendOpportunity


class ContentBrief(BaseModel):
    """A compact, reviewable plan for one social post."""

    topic: str
    platform: str = "instagram"
    audience: str = "People interested in practical, customizable 3D-printed products"
    angle: str
    format: str = "reel"
    call_to_action: str = "DM GenForge to discuss a custom design"
    evidence: list[str] = Field(default_factory=list)
    requires_human_review: bool = True


def build_brief(item: TrendOpportunity) -> ContentBrief:
    """Create a deterministic brief; AI-assisted copy generation comes later."""
    evidence = [f"Source: {item.source}"]
    if item.views is not None:
        evidence.append(f"Views observed: {item.views}")
    if item.likes is not None:
        evidence.append(f"Likes observed: {item.likes}")
    if item.comments is not None:
        evidence.append(f"Comments observed: {item.comments}")

    return ContentBrief(
        topic=item.topic,
        angle=f"Show how GenForge could turn the idea behind {item.topic} into a customizable 3D-printed product.",
        evidence=evidence,
    )
