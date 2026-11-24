import json
from genforge_marketing.intelligence.campaign_execution_plan import campaign_plan
from genforge_marketing.intelligence.campaign_workspace import create_campaign_workspace

def test_execution_plan_suggests_research(tmp_path):
    create_campaign_workspace(tmp_path, "Campaign", "Product")
    plan = campaign_plan(tmp_path / "campaign")
    assert plan["next_stage"] == "research"
    assert "Collect product context" in plan["next_action"]
    assert plan["automated_side_effects"] is False

def test_plan_lists_declared_missing_artifact_for_current_stage(tmp_path):
    create_campaign_workspace(tmp_path, "Campaign", "Product")
    folder=tmp_path/"campaign"
    manifest=json.loads((folder/"campaign.json").read_text())
    manifest["artifacts"]={"research":["research-notes.md"]}
    (folder/"campaign.json").write_text(json.dumps(manifest),encoding="utf-8")
    plan=campaign_plan(folder)
    assert plan["missing_artifacts_for_next_stage"][0]["path"]=="research-notes.md"

def test_plan_requires_human_approval_at_review_stage(tmp_path):
    create_campaign_workspace(tmp_path, "Campaign", "Product")
    folder=tmp_path/"campaign"
    manifest=json.loads((folder/"campaign.json").read_text())
    manifest["progress"]={key:"completed" for key in ["research","analysis","brief","storyboard","production"]}
    (folder/"campaign.json").write_text(json.dumps(manifest),encoding="utf-8")
    plan=campaign_plan(folder)
    assert plan["next_stage"]=="review"
    assert plan["approval_required"] is True
