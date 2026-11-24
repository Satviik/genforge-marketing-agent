from genforge_marketing.intelligence.campaign_pack import build_campaign_pack, write_campaign_pack


def test_campaign_pack_creates_brief_and_claude_handoff(tmp_path):
    pack = build_campaign_pack("Custom bookmark", "Personalized gift", objective="inquiries", duration_seconds=15,
                              creative_breakdown={"phases": [{"role": "hook"}], "adaptation_guidance": ["mechanic only"]})
    assert pack["status"] == "draft_for_review"
    assert pack["external_model_called"] is False
    assert "Custom bookmark" in pack["claude_handoff_markdown"]
    brief_path, handoff_path = write_campaign_pack(pack, tmp_path / "brief.json", tmp_path / "handoff.md")
    assert brief_path.exists() and handoff_path.exists()
    assert "GenForge Creative Production Handoff" in handoff_path.read_text()
