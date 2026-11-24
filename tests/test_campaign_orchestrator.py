from genforge_marketing.intelligence.campaign_orchestrator import load_campaign, status_report, update_stage
from genforge_marketing.intelligence.campaign_workspace import create_campaign_workspace

def test_campaign_status_reports_first_pending_stage(tmp_path):
    create_campaign_workspace(tmp_path, "Campaign", "Product")
    file = tmp_path / "campaign" / "campaign.json"
    campaign = load_campaign(file)
    report = status_report(campaign)
    assert report["next_stage"] == "research"
    update_stage(file, "research", "completed")
    assert status_report(load_campaign(file))["next_stage"] == "analysis"

def test_stage_update_validates_inputs(tmp_path):
    create_campaign_workspace(tmp_path, "Campaign", "Product")
    file = tmp_path / "campaign" / "campaign.json"
    try:
        update_stage(file, "unknown", "completed")
    except ValueError as exc:
        assert "Unknown campaign stage" in str(exc)
    else:
        assert False, "expected invalid stage to raise"

def test_publishing_stage_requires_human_approval(tmp_path):
    create_campaign_workspace(tmp_path, "Approval gate", "Product")
    file=tmp_path/"approval-gate"/"campaign.json"
    try:
        update_stage(file, "published", "in_progress")
    except ValueError as exc:
        assert "human review approval" in str(exc)
    else:
        assert False, "publishing must be gated"

def test_publishing_allowed_after_explicit_approval(tmp_path):
    create_campaign_workspace(tmp_path, "Approval gate", "Product")
    file=tmp_path/"approval-gate"/"campaign.json"
    campaign=load_campaign(file)
    campaign["status"]="approved_for_production"
    campaign["review_record"]={"decision":"approved"}
    file.write_text(__import__("json").dumps(campaign))
    updated=update_stage(file, "published", "in_progress")
    assert updated["progress"]["published"]=="in_progress"
