from genforge_marketing.intelligence.creative_insights import build_creative_insights


def test_insights_rank_creatives_and_include_cautious_test_ideas():
    report = {"creatives": [
        {"creative_id": "a", "rates": {"share_rate": 0.1, "inquiry_rate": 0.02}},
        {"creative_id": "b", "rates": {"share_rate": 0.03, "inquiry_rate": 0.01}},
    ]}
    result = build_creative_insights(report)
    assert result["metric_summaries"]["share_rate"]["ranked"][0]["creative_id"] == "a"
    assert result["test_ideas"]
    assert "do not prove" in result["limitations"][1].lower()


def test_insights_encourage_more_data_for_small_sample():
    result = build_creative_insights({"creatives": []})
    assert any(item["type"] == "data_quality" for item in result["recommendations"])
