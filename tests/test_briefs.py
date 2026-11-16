from genforge_marketing.content.briefs import build_brief
from genforge_marketing.models.opportunity import TrendOpportunity


def test_brief_requires_human_review() -> None:
    brief = build_brief(TrendOpportunity(topic="#3dprinting", source="instagram"))

    assert brief.platform == "instagram"
    assert brief.requires_human_review is True
    assert "GenForge" in brief.angle
