"""Derive cautious, evidence-based creative testing suggestions from recorded performance."""
from __future__ import annotations

from typing import Any


def _average(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 4) if values else None


def build_creative_insights(report: dict[str, Any]) -> dict[str, Any]:
    """Generate descriptive comparisons and test suggestions; never claim causality."""
    creatives = report.get("creatives", [])
    metric_names = ("engagement_rate", "share_rate", "save_rate", "inquiry_rate", "order_rate", "average_watch_seconds_per_view")
    by_metric: dict[str, list[tuple[str, float]]] = {m: [] for m in metric_names}
    for creative in creatives:
        rates = creative.get("rates", {})
        for metric in metric_names:
            value = rates.get(metric)
            if isinstance(value, (int, float)):
                by_metric[metric].append((creative.get("creative_id", "unknown"), float(value)))
    summaries = {}
    for metric, pairs in by_metric.items():
        pairs.sort(key=lambda p: p[1], reverse=True)
        summaries[metric] = {"available_creatives": len(pairs), "ranked": [{"creative_id": cid, "value": value} for cid, value in pairs], "average": _average([v for _, v in pairs])}
    recommendations = []
    if len(creatives) < 3:
        recommendations.append({"type": "data_quality", "priority": "high", "suggestion": "Record results for at least three creatives before drawing directional comparisons; use similar post-age windows and note audience/spend differences."})
    for metric, pairs in by_metric.items():
        if len(pairs) >= 2:
            best_id, best_val = max(pairs, key=lambda p: p[1])
            worst_id, worst_val = min(pairs, key=lambda p: p[1])
            if best_id != worst_id and best_val > worst_val:
                recommendations.append({"type": "metric_comparison", "metric": metric, "priority": "low", "suggestion": f"Explore what differs between {best_id} (higher observed {metric}) and {worst_id}; design a controlled follow-up rather than assuming the difference is caused by creative structure."})
    test_ideas = [
        "A/B test two distinct hook styles while keeping the product, runtime, posting window and CTA as comparable as possible.",
        "Compare process-heavy versus reveal-heavy edits using similar product types and runtimes.",
        "Test one CTA variation at a time and measure inquiries/orders, not only likes.",
        "Use fixed post-age snapshots (for example 24 hours and 7 days) so performance comparisons are less confounded by time.",
    ]
    return {"schema_version": 1, "report_type": "creative_insights", "basis": "descriptive user-entered snapshots",
        "creative_count": len(creatives), "metric_summaries": summaries,
        "recommendations": recommendations, "test_ideas": test_ideas,
        "limitations": ["These insights are exploratory, not statistically validated.", "Performance differences do not prove creative elements caused outcomes.", "Compare creatives with similar audience, posting conditions, spend and post age."]}
