from datetime import datetime, timezone, timedelta

from genforge_marketing.intelligence.radar import (
    CreativeDNA, Reference, ReferenceStore, TrendSignal, build_report, score_signal
)


def signal(**kwargs):
    base = dict(
        title="Desk setup transformation", platform="Instagram", category="desk-setup",
        views=10000, likes=800, comments=100, shares=50, saves=100,
        creator_followers=20000, data_completeness=0.9,
        published_at=datetime.now(timezone.utc) - timedelta(days=2),
    )
    base.update(kwargs)
    return TrendSignal(**base)


def test_score_is_bounded_and_components_are_transparent():
    result = score_signal(signal())
    assert 0 <= result["score"] <= 1
    assert "engagement" in result["components"]
    assert "relative_reach" in result["components"]


def test_missing_metrics_are_handled():
    result = score_signal(signal(views=None, likes=None, comments=None, shares=None, saves=None, creator_followers=None, published_at=None))
    assert result["score"] == 0.9
    assert result["confidence"] == 0.2


def test_reference_store_round_trip(tmp_path):
    store = ReferenceStore(tmp_path / "radar.db")
    reference = Reference(signal=signal(), dna=CreativeDNA(hook_type="before-after", confidence=0.8))
    ref_id = store.add(reference)
    assert store.get(ref_id)["dna"]["hook_type"] == "before-after"
    assert store.list()[0]["id"] == ref_id


def test_report_ranks_and_discloses_limitations():
    report = build_report([signal(), signal(title="Low data", views=None, data_completeness=0.1)])
    assert report["count"] == 2
    assert len(report["ranked_signals"]) == 2
    assert report["limitations"]


def test_creative_pattern_summary_aggregates_dna():
    from genforge_marketing.intelligence.radar import summarize_creative_patterns

    rows = [
        {"reference": {"dna": {"hook_type": "before-after", " payoff_type": "transformation",
            "visual_patterns": ["macro close-up", "macro close-up"], "editing_patterns": ["quick cuts"],
            "psychological_triggers": ["curiosity"], "adaptable_principles": ["show process"]}}},
        {"reference": {"dna": {"hook_type": "before-after", "payoff_type": "transformation",
            "visual_patterns": ["macro close-up"], "editing_patterns": ["quick cuts"],
            "psychological_triggers": ["curiosity"], "adaptable_principles": ["show process"]}}},
    ]
    summary = summarize_creative_patterns(rows)
    assert summary["reference_count"] == 2
    assert summary["patterns"]["hook_types"][0] == {"pattern": "before-after", "count": 2}
    assert summary["patterns"]["visual_patterns"][0]["pattern"] == "macro close-up"
    assert summary["patterns"]["visual_patterns"][0]["count"] == 3
