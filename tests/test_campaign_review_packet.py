from genforge_marketing.intelligence.campaign_workspace import create_campaign_workspace
from genforge_marketing.intelligence.campaign_pipeline import build_campaign_creative
from genforge_marketing.intelligence.campaign_review_packet import build_campaign_review_packet, export_campaign_review_packet


def test_review_packet_includes_brief_storyboard_and_decision_checklist(tmp_path):
    workspace = create_campaign_workspace(tmp_path, "Review Campaign", "Product")["workspace"]
    build_campaign_creative(workspace)
    packet = build_campaign_review_packet(workspace)
    assert "## Creative brief" in packet["markdown"]
    assert "## Storyboard" in packet["markdown"]
    assert "## Human decision" in packet["markdown"]
    assert "- [ ] Approved for production" in packet["markdown"]
    assert packet["read_only"] is True
    assert packet["approval_required"] is True
    assert packet["publishing_enabled"] is False


def test_review_packet_export_writes_markdown(tmp_path):
    workspace = create_campaign_workspace(tmp_path, "Review Campaign", "Product")["workspace"]
    output = tmp_path / "review" / "packet.md"
    report = export_campaign_review_packet(workspace, output)
    assert output.exists()
    assert report["output_path"] == str(output)
    assert "No creative brief found." in output.read_text(encoding="utf-8")
