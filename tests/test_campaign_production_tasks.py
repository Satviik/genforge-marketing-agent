import json
from pathlib import Path
import pytest
from genforge_marketing.intelligence.campaign_workspace import create_campaign_workspace
from genforge_marketing.intelligence.campaign_pipeline import build_campaign_creative
from genforge_marketing.intelligence.campaign_review_decision import record_campaign_review
from genforge_marketing.intelligence.campaign_production_handoff import create_production_handoff
from genforge_marketing.intelligence.campaign_production_tasks import add_production_task, update_production_task, list_production_tasks

def ready_campaign(tmp_path):
    folder=create_campaign_workspace(tmp_path,"Tasks Campaign","Product")["workspace"]
    build_campaign_creative(folder); record_campaign_review(folder,"Reviewer","approved","ok"); create_production_handoff(folder)
    return folder

def test_add_and_list_task(tmp_path):
    folder=ready_campaign(tmp_path)
    task=add_production_task(folder,"Film product close-up","Show details","Satvik","high","2026-12-01")
    result=list_production_tasks(folder)
    assert task["task_id"]=="task-001" and task["status"]=="todo"
    assert result["count"]==1 and result["tasks"][0]["assignee"]=="Satvik"

def test_update_task_status(tmp_path):
    folder=ready_campaign(tmp_path)
    task=add_production_task(folder,"Edit reel")
    updated=update_production_task(folder,task["task_id"],"in_progress","Editing started")
    assert updated["status"]=="in_progress" and updated["notes"]=="Editing started"

def test_tasks_require_approval(tmp_path):
    folder=create_campaign_workspace(tmp_path,"Campaign","Product")["workspace"]
    with pytest.raises(ValueError,match="explicit campaign approval"):
        add_production_task(folder,"Task")

def test_task_validations(tmp_path):
    folder=ready_campaign(tmp_path)
    with pytest.raises(ValueError,match="Task title"):
        add_production_task(folder," ")
    with pytest.raises(ValueError,match="Priority"):
        add_production_task(folder,"Task",priority="urgent")
    with pytest.raises(ValueError,match="Due date"):
        add_production_task(folder,"Task",due_date="bad-date")
    with pytest.raises(ValueError,match="not found"):
        update_production_task(folder,"missing","completed")
