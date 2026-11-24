"""Persistent trend snapshots and simple historical velocity calculations."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .radar import TrendSignal


def stable_signal_id(signal: TrendSignal) -> str:
    """Create a stable ID from URL when available, otherwise normalized platform/title."""
    key = str(signal.url).strip().lower() if signal.url else f"{signal.platform.strip().lower()}:{signal.title.strip().lower()}"
    return "trend-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


class TrendHistoryStore:
    """SQLite store for repeated signal observations (one row per signal/time)."""

    def __init__(self, path: Path = Path("data/trend-history.sqlite")) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS trend_snapshots (
                signal_id TEXT NOT NULL,
                observed_at TEXT NOT NULL,
                signal_json TEXT NOT NULL,
                PRIMARY KEY(signal_id, observed_at)
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_trend_snapshots_id ON trend_snapshots(signal_id, observed_at)")

    def record(self, signal: TrendSignal) -> str:
        signal_id = stable_signal_id(signal)
        observed_at = signal.collected_at.astimezone(timezone.utc).isoformat()
        payload = signal.model_dump_json()
        with sqlite3.connect(self.path) as db:
            db.execute(
                "INSERT OR REPLACE INTO trend_snapshots(signal_id, observed_at, signal_json) VALUES (?, ?, ?)",
                (signal_id, observed_at, payload),
            )
        return signal_id

    def snapshots(self, signal_id: str) -> list[TrendSignal]:
        with sqlite3.connect(self.path) as db:
            rows = db.execute(
                "SELECT signal_json FROM trend_snapshots WHERE signal_id=? ORDER BY observed_at ASC",
                (signal_id,),
            ).fetchall()
        return [TrendSignal.model_validate_json(row[0]) for row in rows]

    def compare(self, signal_id: str) -> dict[str, Any]:
        history = self.snapshots(signal_id)
        if len(history) < 2:
            return {"signal_id": signal_id, "snapshots": len(history), "velocity": None,
                    "message": "At least two distinct snapshots are required to estimate velocity."}
        first, latest = history[0], history[-1]
        elapsed = (latest.collected_at - first.collected_at).total_seconds() / 86400
        if elapsed <= 0:
            return {"signal_id": signal_id, "snapshots": len(history), "velocity": None,
                    "message": "Snapshots must span positive elapsed time to estimate velocity."}
        metrics = {}
        for field in ("views", "likes", "comments", "shares"):
            a, b = getattr(first, field), getattr(latest, field)
            metrics[field] = None if a is None or b is None else {
                "start": a, "latest": b, "delta": b - a, "per_day": round((b - a) / elapsed, 2)
            }
        return {"signal_id": signal_id, "snapshots": len(history), "elapsed_days": round(elapsed, 3),
                "first_observed": first.collected_at.isoformat(), "latest_observed": latest.collected_at.isoformat(),
                "velocity": metrics, "note": "Velocity is descriptive snapshot change, not a prediction."}
