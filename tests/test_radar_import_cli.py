import json

from typer.testing import CliRunner

from genforge_marketing.cli import app


def test_radar_import_screening_maps_metadata(tmp_path) -> None:
    export = tmp_path / "screening.json"
    output = tmp_path / "report.json"
    export.write_text(
        json.dumps({
            "source_agent": "gen-forge-screening-agent",
            "items": [{
                "topic": "3D printed desk organizer",
                "source": "instagram",
                "source_url": "https://example.com/reel",
                "summary": "A modular desk organizer",
                "views": 1500,
                "likes": 120,
                "comments": 8,
                "observed_at": "2026-11-20T12:00:00Z",
                "raw": {
                    "creator": "demo_creator",
                    "search_term": "#desksetup",
                    "published_at": "2026-11-18T12:00:00Z",
                    "shares": 14,
                },
            }],
        }),
        encoding="utf-8",
    )
    result = CliRunner().invoke(
        app,
        ["radar", "import-screening", "--input", str(export), "--output", str(output)],
    )
    assert result.exit_code == 0, result.output
    report = json.loads(output.read_text(encoding="utf-8"))
    signal = report["ranked_signals"][0]["signal"]
    assert signal["creator"] == "demo_creator"
    assert signal["category"] == "#desksetup"
    assert signal["shares"] == 14
    assert signal["published_at"] == "2026-11-18T12:00:00Z"
    assert signal["data_completeness"] > 0.75
    history = report["history"]
    assert history["recorded_snapshots"] == 1
    assert len(history["signal_ids"]) == 1
    from genforge_marketing.intelligence.trend_history import TrendHistoryStore
    snapshots = TrendHistoryStore(tmp_path / "trend-history.sqlite").snapshots(history["signal_ids"][0])
    assert len(snapshots) == 1
    assert snapshots[0].views == 1500
