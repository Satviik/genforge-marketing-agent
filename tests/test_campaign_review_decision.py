import json
from pathlib import Path
import pytest
from genforge_marketing.intelligence.campaign_workspace import create_campaign_workspace
from genforge_marketing.intelligence.campaign_pipeline import build_campaign_creative
from genforge_marketing.intelligence.campaign_review_decision import record_campaign_review


def test_approval_requires_ready_gate_and_records_review(tmp_path):
    folder=create_campaign_workspace(tmp_path,"Campaign","Product")["workspace"]
    build_campaign_creative(folder)
    result=record_campaign_review(folder,"Reviewer","approved","Looks good.")
    data=json.loads((Path(folder)/"campaign.json").read_text())
    assert result["decision"]=="approved"
    assert result["reviewer"]=="Reviewer"
    assert data["progress"]["review"]=="approved"
    assert data["status"]=="approved_for_production"
    assert data["review_record"]["notes"]=="Looks good."


def test_approval_blocked_when_campaign_not_ready(tmp_path):
    folder=create_campaign_workspace(tmp_path,"Campaign","Product")["workspace"]
    with pytest.raises(ValueError,match="not ready"):
        record_campaign_review(folder,"Reviewer","approved")


def test_changes_requested_returns_campaign_for_revision(tmp_path):
    folder=create_campaign_workspace(tmp_path,"Campaign","Product")["workspace"]
    result=record_campaign_review(folder,"Reviewer","changes_requested","Change CTA")
    data=json.loads((Path(folder)/"campaign.json").read_text())
    assert result["decision"]=="changes_requested"
    assert data["progress"]["review"]=="in_progress"
    assert data["status"]=="needs_changes"
