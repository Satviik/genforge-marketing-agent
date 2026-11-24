import json
from pathlib import Path
import pytest
from genforge_marketing.intelligence.campaign_workspace import create_campaign_workspace
from genforge_marketing.intelligence.campaign_pipeline import build_campaign_creative
from genforge_marketing.intelligence.campaign_review_decision import record_campaign_review
from genforge_marketing.intelligence.campaign_production_handoff import create_production_handoff
from genforge_marketing.intelligence.campaign_production_tracking import update_production_status

def approved_campaign(tmp_path):
    folder=create_campaign_workspace(tmp_path,"Tracking Campaign","Product")["workspace"]
    build_campaign_creative(folder)
    record_campaign_review(folder,"Reviewer","approved","Ready")
    create_production_handoff(folder)
    return Path(folder)

def test_tracking_requires_approval_and_handoff(tmp_path):
    folder=create_campaign_workspace(tmp_path,"Campaign","Product")["workspace"]
    with pytest.raises(ValueError,match="explicit campaign approval"):
        update_production_status(folder,"in_progress")

def test_status_updates_handoff_manifest_without_publishing(tmp_path):
    folder=approved_campaign(tmp_path)
    result=update_production_status(folder,"in_progress","Recording started")
    manifest=json.loads(Path(result["manifest_path"]).read_text())
    assert manifest["production_started"] is True
    assert manifest["publishing_enabled"] is False
    assert manifest["production_tracking"]["status"]=="in_progress"
    assert manifest["production_tracking"]["started_at"]

def test_completed_status_records_completion(tmp_path):
    folder=approved_campaign(tmp_path)
    result=update_production_status(folder,"completed")
    manifest=json.loads(Path(result["manifest_path"]).read_text())
    assert manifest["production_tracking"]["completed_at"]
    assert manifest["production_started"] is True

def test_invalid_status_rejected(tmp_path):
    folder=approved_campaign(tmp_path)
    with pytest.raises(ValueError,match="Status must be one"):
        update_production_status(folder,"published")
