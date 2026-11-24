from genforge_marketing.intelligence.creative_generator import generate_original_reel
from genforge_marketing.intelligence.claude_handoff import render_claude_package


def test_handoff_package_includes_brief_and_reference_evidence():
    brief = generate_original_reel("Personalized bookmark", duration_seconds=15)
    breakdown = {"observed_structure": ["Hook", "Process"], "adaptation_guidance": ["Use mechanics only"]}
    package_text = render_claude_package(brief, creative_breakdown=breakdown)
    assert "GenForge Creative Production Handoff" in package_text
    assert "Personalized bookmark" in package_text
    assert "Do not copy reference wording" in package_text
    assert "Creative Breakdown Evidence" in package_text
    assert "production-ready script" in package_text
