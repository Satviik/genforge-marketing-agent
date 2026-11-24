from genforge_marketing.intelligence.campaign_workspace import create_campaign_workspace

def test_workspace_creates_manifest_folders_and_experiment_template(tmp_path):
    result = create_campaign_workspace(tmp_path, "Bookmark launch", "Custom bookmark", objective="inquiries")
    path = tmp_path / "bookmark-launch"
    assert result["workspace"] == str(path)
    assert (path / "campaign.json").exists()
    assert (path / "experiments" / "experiment-01.json").exists()
    assert (path / "drafts").is_dir()
    assert (path / "README.md").exists()

def test_workspace_slug_fallback_for_empty_name(tmp_path):
    result = create_campaign_workspace(tmp_path, "!!!", "Product")
    assert result["workspace"].endswith("campaign")
