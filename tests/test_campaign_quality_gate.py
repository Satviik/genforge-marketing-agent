import json
from genforge_marketing.intelligence.campaign_workspace import create_campaign_workspace
from genforge_marketing.intelligence.campaign_pipeline import build_campaign_creative
from genforge_marketing.intelligence.campaign_quality_gate import quality_gate

def test_quality_gate_passes_generated_draft_except_review(tmp_path):
 create_campaign_workspace(tmp_path,"Campaign","Product")
 folder=tmp_path/"campaign"
 build_campaign_creative(folder)
 report=quality_gate(folder)
 assert report["failed"] >= 1
 assert report["approval_required"] is True
 assert report["automated_publish_allowed"] is False
 assert any(c["name"]=="human_review_recorded" and not c["passed"] for c in report["checks"])

def test_gate_detects_missing_storyboard(tmp_path):
 create_campaign_workspace(tmp_path,"Campaign","Product")
 report=quality_gate(tmp_path/"campaign")
 assert any(c["name"]=="storyboard_exists" and not c["passed"] for c in report["checks"])

def test_gate_detects_invalid_scene_timeline(tmp_path):
 create_campaign_workspace(tmp_path,"Campaign","Product")
 folder=tmp_path/"campaign"
 build_campaign_creative(folder)
 brief_path=folder/"drafts"/"creative-brief.json"
 brief=json.loads(brief_path.read_text())
 brief["production_plan"]["scenes"][1]["start_seconds"]+=1
 brief_path.write_text(json.dumps(brief),encoding="utf-8")
 report=quality_gate(folder)
 assert any(c["name"]=="timeline_contiguous" and not c["passed"] for c in report["checks"])
