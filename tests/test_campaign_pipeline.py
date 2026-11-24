import json
from genforge_marketing.intelligence.campaign_workspace import create_campaign_workspace
from genforge_marketing.intelligence.campaign_pipeline import build_campaign_creative

def test_pipeline_creates_brief_storyboard_and_registers_artifacts(tmp_path):
 create_campaign_workspace(tmp_path,"Bookmark Launch","Personalized bookmark",objective="inquiries",audience="book lovers")
 folder=tmp_path/"bookmark-launch"
 result=build_campaign_creative(folder,20)
 brief=json.loads((folder/"drafts"/"creative-brief.json").read_text())
 manifest=json.loads((folder/"campaign.json").read_text())
 assert result["scene_count"]==6
 assert (folder/"production"/"storyboard.md").exists()
 assert "drafts/creative-brief.json" in manifest["artifacts"]["brief"]
 assert manifest["progress"]["brief"]=="in_progress"
 assert brief["provider"]=="deterministic_local_template"

def test_pipeline_refuses_overwrite(tmp_path):
 create_campaign_workspace(tmp_path,"Campaign","Product")
 folder=tmp_path/"campaign"
 build_campaign_creative(folder)
 try:
  build_campaign_creative(folder)
 except FileExistsError as exc:
  assert "Refusing to overwrite" in str(exc)
 else:
  assert False,"Expected overwrite refusal"
