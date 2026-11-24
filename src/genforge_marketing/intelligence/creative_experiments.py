"""Compare planned creative experiments using recorded latest metrics."""
from __future__ import annotations

from typing import Any


def compare_experiment(experiment: dict[str, Any], feedback_report: dict[str, Any]) -> dict[str, Any]:
    """Descriptive comparison of creatives grouped by declared experiment variant."""
    variants = experiment.get("variants", [])
    creatives = {c.get("creative_id"): c for c in feedback_report.get("creatives", [])}
    metric_keys = ("engagement_rate", "share_rate", "save_rate", "inquiry_rate", "order_rate", "average_watch_seconds_per_view")
    result_variants = []
    for variant in variants:
        name = str(variant.get("name", "unnamed"))
        ids = variant.get("creative_ids", [])
        matched = [creatives[cid] for cid in ids if cid in creatives]
        summaries = {}
        for metric in metric_keys:
            values = [c.get("rates", {}).get(metric) for c in matched]
            values = [float(v) for v in values if isinstance(v, (int, float))]
            summaries[metric] = {"sample_count": len(values), "mean": round(sum(values) / len(values), 4) if values else None}
        result_variants.append({"name": name, "creative_ids": ids, "matched_creatives": len(matched), "metrics": summaries})
    winners = {}
    for metric in metric_keys:
        valid = [(v["name"], v["metrics"][metric]["mean"], v["metrics"][metric]["sample_count"]) for v in result_variants if v["metrics"][metric]["mean"] is not None]
        winners[metric] = {"observed_leader": max(valid, key=lambda x: x[1])[0] if valid else None, "variant_means": {name: mean for name, mean, _ in valid}}
    return {"schema_version": 1, "report_type": "creative_experiment_comparison", "experiment_id": experiment.get("experiment_id"),
        "hypothesis": experiment.get("hypothesis"), "variable_tested": experiment.get("variable_tested"),
        "status": experiment.get("status", "planned"), "variants": result_variants, "metric_leaders": winners,
        "interpretation": "Descriptive comparison only. The observed leader is not proof of a causal effect.",
        "warnings": ["Keep observation windows, audience, spend and posting conditions comparable.", "Interpret cautiously when variants have fewer than three creatives or incomplete metrics."]}
