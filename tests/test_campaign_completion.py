import json
from genforge_marketing.intelligence.campaign_workspace import create_campaign_workspace
from genforge_marketing.intelligence.campaign_completion import campaign_completion_report

def test_incomplete_campaign_report_has_issues(tmp_path):
    workspace=create_campaign_workspace(tmp_path,"Final audit","Bookmark")["workspace"]
    report=campaign_completion_report(workspace)
    assert not report["complete"]
    assert report["issue_count"]>=4
    assert report["read_only"] and report["automated_publishing"] is False

def test_completed_campaign_report(tmp_path):
    workspace=create_campaign_workspace(tmp_path,"Final audit","Bookmark")["workspace"]
    path=tmp_path/"final-audit"/"campaign.json"
    path.parent.mkdir()
    campaign=json.loads((__import__("pathlib").Path(workspace)/"campaign.json").read_text())
    campaign["status"]="approved_for_production"
    campaign["review_record"]={"decision":"approved"}
    campaign["progress"]={"published":"completed","metrics":"completed","learning":"completed"}
    path.write_text(json.dumps(campaign))
    handoff=path.parent/"production"/"handoff"
    handoff.mkdir(parents=True)
    (handoff/"handoff.json").write_text(json.dumps({"production_tasks":[{"task_id":"t1","title":"Film","status":"completed"}],"assets":[{"asset_id":"a1","name":"Hero","status":"approved"}]}))
    report=campaign_completion_report(path)
    assert report["complete"] and report["issue_count"]==0
    assert report["summary"]["approved_assets"]==1
