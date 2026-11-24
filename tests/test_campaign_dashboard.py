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



def test_dashboard_separates_human_review_from_blockers(tmp_path):
    from genforge_marketing.intelligence.campaign_pipeline import build_campaign_creative

    workspace = create_campaign_workspace(tmp_path, "Review Campaign", "Product")["workspace"]
    build_campaign_creative(workspace)
    result = campaign_dashboard(workspace)
    assert result["readiness"] == "ready_for_human_review"
    assert result["blocker_count"] == 0
    assert any(item["check"] == "human_review_recorded" for item in result["review_items"])
    assert result["human_approval_required"] is True
    assert result["automated_publishing"] is False



def test_dashboard_reports_production_handoff_state(tmp_path):
    workspace = create_campaign_workspace(tmp_path, "Campaign", "Product")["workspace"]
    before = campaign_dashboard(workspace)
    assert before["production_handoff"]["status"] == "not_created"
    handoff = tmp_path / "campaign" / "production" / "handoff"
    handoff.mkdir(parents=True)
    (handoff / "handoff.json").write_text("{}", encoding="utf-8")
    after = campaign_dashboard(workspace)
    assert after["production_handoff"]["status"] == "created"
    assert after["production_handoff"]["production_started"] is False
    assert after["production_handoff"]["publishing_enabled"] is False


def test_dashboard_reads_production_tracking_state(tmp_path):
    workspace = create_campaign_workspace(tmp_path, "Campaign", "Product")["workspace"]
    handoff = tmp_path / "campaign" / "production" / "handoff"
    handoff.mkdir(parents=True)
    (handoff / "handoff.json").write_text(json.dumps({"production_tracking": {"status": "in_progress", "notes": "Filming"}}), encoding="utf-8")
    report = campaign_dashboard(workspace)
    assert report["production_handoff"]["tracking"]["status"] == "in_progress"
    assert report["production_handoff"]["publishing_enabled"] is False


def test_dashboard_summarizes_production_tasks(tmp_path):
    workspace = create_campaign_workspace(tmp_path, "Campaign", "Product")["workspace"]
    handoff = tmp_path / "campaign" / "production" / "handoff"
    handoff.mkdir(parents=True)
    (handoff / "handoff.json").write_text(json.dumps({"production_tasks": [
        {"status": "todo"}, {"status": "in_progress"}, {"status": "completed"}, {"status": "blocked"}
    ]}), encoding="utf-8")
    result = campaign_dashboard(workspace)
    assert result["production_handoff"]["tasks"] == {
        "count": 4, "completed": 1, "in_progress": 1, "blocked": 1, "todo": 1
    }


def test_dashboard_summarizes_campaign_assets(tmp_path):
    workspace=create_campaign_workspace(tmp_path,"Campaign","Product")["workspace"]
    handoff=tmp_path/"campaign"/"production"/"handoff"
    handoff.mkdir(parents=True)
    (handoff/"handoff.json").write_text(json.dumps({"assets":[
        {"status":"draft","revision":1},{"status":"approved","revision":3},{"status":"rejected","revision":2}
    ]}),encoding="utf-8")
    report=campaign_dashboard(workspace)
    assert report["production_handoff"]["assets"] == {
        "count":3,"draft":1,"review":0,"approved":1,"rejected":1,"revisions":6
    }
