from datetime import datetime, timezone
import pytest

from genforge_marketing.intelligence.creative_feedback import CreativeFeedbackStore


def test_feedback_records_and_reports_metrics(tmp_path):
    store = CreativeFeedbackStore(tmp_path / "feedback.db")
    store.record("reel-001", "Instagram", {"views": 1000, "reach": 800, "likes": 100, "comments": 10, "shares": 20, "saves": 30, "inquiries": 4, "orders": 1, "revenue_inr": 499}, {"hook": "reveal"})
    report = store.report()
    assert report["creative_count"] == 1
    rates = report["creatives"][0]["rates"]
    assert rates["engagement_rate"] == pytest.approx(0.2)
    assert rates["inquiry_rate"] == pytest.approx(0.005)
    assert report["creatives"][0]["tags"]["hook"] == "reveal"


def test_feedback_rejects_invalid_metrics(tmp_path):
    store = CreativeFeedbackStore(tmp_path / "feedback.db")
    with pytest.raises(ValueError):
        store.record("reel", "Instagram", {"views": -1})
    with pytest.raises(ValueError):
        store.record("reel", "Instagram", {"unknown_metric": 1})


def test_aggregate_uses_latest_snapshot_per_creative(tmp_path):
    store = CreativeFeedbackStore(tmp_path / "feedback.db")
    store.record("reel-001", "Instagram", {"views": 100}, observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
    store.record("reel-001", "Instagram", {"views": 250}, observed_at=datetime(2026, 1, 2, tzinfo=timezone.utc))
    report = store.report()
    assert report["snapshot_count"] == 2
    assert report["aggregate_latest_creatives"]["views"] == 250
