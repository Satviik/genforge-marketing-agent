import json
import pytest
from pathlib import Path
from genforge_marketing.intelligence.campaign_workspace import create_campaign_workspace
from genforge_marketing.intelligence.campaign_pipeline import build_campaign_creative
from genforge_marketing.intelligence.campaign_review_decision import record_campaign_review
from genforge_marketing.intelligence.campaign_production_handoff import create_production_handoff

def test_handoff_requires_explicit_approval(tmp_path):
    folder=create_campaign_workspace(tmp_path,"Campaign","Product")["workspace"]
    with pytest.raises(ValueError,match="explicit recorded approval"):
        create_production_handoff(folder)

def test_approved_campaign_creates_non_publishing_handoff(tmp_path):
    folder=create_campaign_workspace(tmp_path,"Campaign","Product")["workspace"]
    build_campaign_creative(folder)
    record_campaign_review(folder,"Reviewer","approved","Ready")
    result=create_production_handoff(folder)
    assert Path(result["manifest_path"]).exists()
    assert (Path(result["handoff_dir"])/"creative-brief.json").exists()
    assert (Path(result["handoff_dir"])/"storyboard.md").exists()
    manifest=json.loads(Path(result["manifest_path"]).read_text())
    assert manifest["production_started"] is False
    assert manifest["publishing_enabled"] is False

def test_handoff_requires_brief_and_storyboard(tmp_path):
    folder=create_campaign_workspace(tmp_path,"Campaign","Product")["workspace"]
    build_campaign_creative(folder)
    record_campaign_review(folder,"Reviewer","approved","Approved")
    (Path(folder)/"production"/"storyboard.md").unlink()
    with pytest.raises(ValueError,match="creative brief JSON and storyboard"):
        create_production_handoff(folder)
