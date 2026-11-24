from genforge_marketing.intelligence.creative_experiments import compare_experiment


def test_experiment_report_compares_variant_means():
    experiment = {"experiment_id": "hook-01", "hypothesis": "Reveal hooks may earn more shares", "variable_tested": "hook", "variants": [
        {"name": "reveal", "creative_ids": ["a", "b"]}, {"name": "question", "creative_ids": ["c"]}]}
    feedback = {"creatives": [
        {"creative_id": "a", "rates": {"share_rate": 0.08}},
        {"creative_id": "b", "rates": {"share_rate": 0.06}},
        {"creative_id": "c", "rates": {"share_rate": 0.02}}]}
    report = compare_experiment(experiment, feedback)
    assert report["metric_leaders"]["share_rate"]["observed_leader"] == "reveal"
    assert report["variants"][0]["metrics"]["share_rate"]["mean"] == 0.07
    assert "not proof" in report["interpretation"].lower()


def test_experiment_report_handles_missing_creatives():
    report = compare_experiment({"experiment_id": "empty", "variants": [{"name": "A", "creative_ids": ["missing"]}]}, {"creatives": []})
    assert report["variants"][0]["matched_creatives"] == 0
    assert report["metric_leaders"]["share_rate"]["observed_leader"] is None
