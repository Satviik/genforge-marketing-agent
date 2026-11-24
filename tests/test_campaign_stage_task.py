from genforge_marketing.intelligence.campaign_workspace import create_campaign_workspace
from genforge_marketing.intelligence.campaign_stage_task import create_stage_task

def test_create_stage_task_for_next_stage(tmp_path):
 create_campaign_workspace(tmp_path,"Campaign","Product")
 result=create_stage_task(tmp_path/"campaign")
 assert result["stage"]=="research"
 assert (tmp_path/"campaign"/"observations"/"research-notes.md").exists()

def test_task_creation_refuses_overwrite(tmp_path):
 create_campaign_workspace(tmp_path,"Campaign","Product")
 create_stage_task(tmp_path/"campaign","research")
 try:
  create_stage_task(tmp_path/"campaign","research")
 except FileExistsError as exc:
  assert "refusing to overwrite" in str(exc)
 else:
  assert False, "expected overwrite refusal"

def test_stage_task_does_not_change_campaign_progress(tmp_path):
 create_campaign_workspace(tmp_path,"Campaign","Product")
 create_stage_task(tmp_path/"campaign","brief")
 import json
 manifest=json.loads((tmp_path/"campaign"/"campaign.json").read_text())
 assert "progress" not in manifest
