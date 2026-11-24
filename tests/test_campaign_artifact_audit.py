import json
from genforge_marketing.intelligence.campaign_artifact_audit import audit_artifacts
from genforge_marketing.intelligence.campaign_workspace import create_campaign_workspace

def test_artifact_audit_reports_missing_and_present(tmp_path):
    create_campaign_workspace(tmp_path, "Campaign", "Product")
    folder = tmp_path / "campaign"
    (folder / "brief.md").write_text("brief", encoding="utf-8")
    manifest = json.loads((folder / "campaign.json").read_text())
    manifest["artifacts"] = {"brief": ["brief.md", "storyboard.html"]}
    (folder / "campaign.json").write_text(json.dumps(manifest), encoding="utf-8")
    report = audit_artifacts(folder)
    assert report["checked_count"] == 2
    assert report["existing_count"] == 1
    assert report["missing"][0]["path"] == "storyboard.html"

def test_empty_artifact_list_audits_cleanly(tmp_path):
    create_campaign_workspace(tmp_path, "Campaign", "Product")
    report = audit_artifacts(tmp_path / "campaign")
    assert report["checked_count"] == 0
    assert report["missing_count"] == 0

def test_artifact_audit_rejects_parent_traversal(tmp_path):
    create_campaign_workspace(tmp_path, "Campaign", "Product")
    folder = tmp_path / "campaign"
    manifest = json.loads((folder / "campaign.json").read_text())
    manifest["artifacts"] = {"brief": ["../outside.txt"]}
    (folder / "campaign.json").write_text(json.dumps(manifest), encoding="utf-8")
    try:
        audit_artifacts(folder)
    except ValueError as exc:
        assert "stay inside" in str(exc)
    else:
        assert False, "expected path traversal rejection"
