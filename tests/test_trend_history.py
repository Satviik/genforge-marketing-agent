from datetime import datetime, timezone, timedelta

from genforge_marketing.intelligence.radar import TrendSignal
from genforge_marketing.intelligence.trend_history import TrendHistoryStore, stable_signal_id


def mk_signal(at, views):
    return TrendSignal(title="Modular desk organizer", platform="Instagram", views=views,
                      collected_at=at, data_completeness=0.8)


def test_stable_ids_and_snapshot_velocity(tmp_path):
    store = TrendHistoryStore(tmp_path / "history.db")
    start = datetime(2026, 11, 20, tzinfo=timezone.utc)
    a, b = mk_signal(start, 100), mk_signal(start + timedelta(days=2), 500)
    assert stable_signal_id(a) == stable_signal_id(b)
    signal_id = store.record(a)
    store.record(b)
    result = store.compare(signal_id)
    assert result["snapshots"] == 2
    assert result["velocity"]["views"]["delta"] == 400
    assert result["velocity"]["views"]["per_day"] == 200


def test_velocity_requires_two_snapshots(tmp_path):
    store = TrendHistoryStore(tmp_path / "history.db")
    signal_id = store.record(mk_signal(datetime.now(timezone.utc), 12))
    assert store.compare(signal_id)["velocity"] is None
