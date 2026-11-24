from genforge_marketing.intelligence.campaign_workspace import create_campaign_workspace
from genforge_marketing.intelligence.campaign_dashboard import campaign_dashboard

def test_dashboard_combines_status_artifacts_and_quality(tmp_path):
 create_campaign_workspace(tmp_path,"Campaign","Product")
 result=campaign_dashboard(tmp_path/"campaign")
 assert result["next_stage"]=="research"
 assert "artifact_summary" in result and "quality_summary" in result
 assert result["read_only"] is True
 assert result["automated_publishing"] is False
