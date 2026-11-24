from pathlib import Path
import json
import pytest
from genforge_marketing.intelligence.campaign_workspace import create_campaign_workspace
from genforge_marketing.intelligence.campaign_pipeline import build_campaign_creative
from genforge_marketing.intelligence.campaign_review_decision import record_campaign_review
from genforge_marketing.intelligence.campaign_production_handoff import create_production_handoff
from genforge_marketing.intelligence.campaign_asset_tracker import add_campaign_asset, revise_campaign_asset, set_campaign_asset_status, list_campaign_assets

def ready(tmp_path):
    folder=create_campaign_workspace(tmp_path,"Asset Campaign","Product")["workspace"]
    build_campaign_creative(folder);record_campaign_review(folder,"Reviewer","approved","ok");create_production_handoff(folder)
    return Path(folder)

def test_asset_add_revision_and_status(tmp_path):
    campaign=ready(tmp_path); source=tmp_path/"mockup.png";source.write_bytes(b"asset-one")
    asset=add_campaign_asset(campaign,source,"Product mockup","image","initial")
    assert asset["revision"]==1 and asset["status"]=="draft"
    rev=tmp_path/"new_mockup.png";rev.write_bytes(b"asset-two")
    updated=revise_campaign_asset(campaign,asset["asset_id"],rev,"updated mockup")
    assert updated["revision"]==2 and len(updated["history"])==2
    status=set_campaign_asset_status(campaign,asset["asset_id"],"approved","looks good")
    assert status["status"]=="approved"
    report=list_campaign_assets(campaign)
    assert report["count"]==1 and report["assets"][0]["revision"]==2
    manifest=json.loads(Path(report["manifest_path"]).read_text())
    assert len(manifest["assets"][0]["status_history"])==1

def test_asset_validation_and_missing_asset(tmp_path):
    campaign=ready(tmp_path)
    with pytest.raises(ValueError,match="Asset file not found"):
        add_campaign_asset(campaign,tmp_path/"missing.png")
    source=tmp_path/"asset.png";source.write_bytes(b"x")
    asset=add_campaign_asset(campaign,source)
    with pytest.raises(ValueError,match="not found"):
        set_campaign_asset_status(campaign,"missing","approved")
    with pytest.raises(ValueError,match="one of"):
        set_campaign_asset_status(campaign,asset["asset_id"],"wrong")
    with pytest.raises(ValueError,match="not found"):
        revise_campaign_asset(campaign,"missing",source)
