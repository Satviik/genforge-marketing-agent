import json

from genforge_marketing.intelligence.campaign_workspace import create_campaign_workspace
from genforge_marketing.intelligence.campaign_dashboard import campaign_dashboard


def test_dashboard_combines_status_artifacts_and_quality(tmp_path):
    create_campaign_workspace(tmp_path, "Campaign", "Product")
    result = campaign_dashboard(tmp_path / "campaign")
    assert result["next_stage"] == "research"
    assert "artifact_summary" in result and "quality_summary" in result
    assert result["read_only"] is True
    assert result["automated_publishing"] is False
    assert result["readiness"] == "blocked"
    assert result["blocker_count"] == len(result["blockers"])
    assert result["blocker_count"] > 0
    assert all(item["suggested_action"] for item in result["blockers"])


def test_dashboard_blockers_include_missing_artifacts_and_quality_checks(tmp_path):
    workspace = create_campaign_workspace(tmp_path, "Campaign", "Product")["workspace"]
    manifest_path = tmp_path / "campaign" / "campaign.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"] = {"research": ["references/research-notes.md"]}
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = campaign_dashboard(workspace)
    types = {item["type"] for item in result["blockers"]}
    assert "missing_artifact" in types
    assert "quality_check" in types
    assert any(item["path"] == "references/research-notes.md" for item in result["blockers"] if item["type"] == "missing_artifact")
