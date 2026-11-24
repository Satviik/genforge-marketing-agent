"""Store performance snapshots for GenForge creatives and summarize observed outcomes."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


METRICS = ("views", "reach", "watch_time_seconds", "likes", "comments", "shares", "saves", "profile_visits", "inquiries", "orders", "revenue_inr")


def _rates(snapshot: dict[str, Any]) -> dict[str, float | None]:
    reach = snapshot.get("reach") or snapshot.get("views")
    views = snapshot.get("views")
    def rate(numerator: str, denominator: Any) -> float | None:
        value = snapshot.get(numerator)
        return round(value / denominator, 4) if value is not None and denominator else None
    return {
        "engagement_rate": round(sum(snapshot.get(k) or 0 for k in ("likes", "comments", "shares", "saves")) / reach, 4) if reach else None,
        "share_rate": rate("shares", reach),
        "save_rate": rate("saves", reach),
        "inquiry_rate": rate("inquiries", reach),
        "order_rate": rate("orders", reach),
        "average_watch_seconds_per_view": rate("watch_time_seconds", views),
    }


class CreativeFeedbackStore:
    def __init__(self, path: Path = Path("data/creative-feedback.sqlite")) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS creative_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT, creative_id TEXT NOT NULL, platform TEXT NOT NULL,
                observed_at TEXT NOT NULL, metrics_json TEXT NOT NULL, tags_json TEXT NOT NULL)""")

    def record(self, creative_id: str, platform: str, metrics: dict[str, Any], tags: dict[str, Any] | None = None, observed_at: datetime | None = None) -> int:
        if not creative_id.strip():
            raise ValueError("creative_id must not be blank")
        if not platform.strip():
            raise ValueError("platform must not be blank")
        for key, value in metrics.items():
            if key not in METRICS:
                raise ValueError(f"unsupported metric: {key}")
            if value is not None and (not isinstance(value, (int, float)) or value < 0):
                raise ValueError(f"metric {key} must be a non-negative number or null")
        timestamp = (observed_at or datetime.now(timezone.utc)).isoformat()
        with sqlite3.connect(self.path) as db:
            cursor = db.execute("INSERT INTO creative_snapshots (creative_id, platform, observed_at, metrics_json, tags_json) VALUES (?, ?, ?, ?, ?)",
                (creative_id.strip(), platform.strip(), timestamp, __import__("json").dumps(metrics), __import__("json").dumps(tags or {})))
            return int(cursor.lastrowid)

    def list_snapshots(self, creative_id: str | None = None) -> list[dict[str, Any]]:
        import json
        with sqlite3.connect(self.path) as db:
            query = "SELECT creative_id, platform, observed_at, metrics_json, tags_json FROM creative_snapshots"
            args: tuple[Any, ...] = ()
            if creative_id:
                query += " WHERE creative_id=?"
                args = (creative_id,)
            query += " ORDER BY observed_at ASC, id ASC"
            rows = db.execute(query, args).fetchall()
        return [{"creative_id": r[0], "platform": r[1], "observed_at": r[2], "metrics": json.loads(r[3]), "tags": json.loads(r[4])} for r in rows]

    def report(self, creative_id: str | None = None) -> dict[str, Any]:
        snapshots = self.list_snapshots(creative_id)
        by_id: dict[str, list[dict[str, Any]]] = {}
        for snap in snapshots:
            by_id.setdefault(snap["creative_id"], []).append(snap)
        creatives = []
        for cid, history in by_id.items():
            first, latest = history[0], history[-1]
            metrics = latest["metrics"]
            creatives.append({"creative_id": cid, "platform": latest["platform"], "snapshots": len(history),
                "first_observed_at": first["observed_at"], "latest_observed_at": latest["observed_at"],
                "latest_metrics": metrics, "rates": _rates(metrics), "tags": latest["tags"],
                "limitations": ["Snapshots are user-entered; comparisons require similar observation windows.", "These descriptive metrics do not establish causal effects."]})
        return {"schema_version": 1, "report_type": "creative_performance_feedback", "creative_count": len(creatives),
            "snapshot_count": len(snapshots), "creatives": creatives,
            "aggregate_observed": {metric: round(sum((s["metrics"].get(metric) or 0) for s in snapshots), 2) if any(s["metrics"].get(metric) is not None for s in snapshots) else None for metric in METRICS},
            "limitations": ["Do not compare posts with different ages, audiences, spend, or formats as if conditions were controlled.", "Metrics are descriptive and cannot prove which creative mechanic caused performance."]}
