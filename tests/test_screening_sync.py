import json
from types import SimpleNamespace

from genforge_marketing.integrations.screening_cli import run_screening_export


def test_run_screening_export_calls_cli_and_parses_json(monkeypatch) -> None:
    payload = {
        "source_agent": "gen-forge-screening-agent",
        "items": [
            {
                "topic": "Custom 3D printed planter",
                "source": "instagram",
                "source_url": "https://www.instagram.com/reel/example/",
                "views": 500,
                "likes": 70,
                "comments": 8,
            }
        ],
    }
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        seen["kwargs"] = kwargs
        return SimpleNamespace(stdout=json.dumps(payload))

    monkeypatch.setattr("genforge_marketing.integrations.screening_cli.subprocess.run", fake_run)

    batch = run_screening_export(command="genforge", timeout_seconds=45, limit=25)

    assert seen["args"] == [
        "genforge", "export", "--output", "-", "--limit", "25"
    ]
    assert seen["kwargs"]["timeout"] == 45
    assert len(batch.items) == 1
    assert batch.items[0].views == 500
    assert batch.items[0].topic == "Custom 3D printed planter"
