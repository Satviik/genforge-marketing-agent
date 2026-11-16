import json

from genforge_marketing.integrations.screening_cli import load_screening_export


def test_load_screening_export(tmp_path) -> None:
    export = tmp_path / "trends.json"
    export.write_text(
        json.dumps(
            {
                "source_agent": "gen-forge-screening-agent",
                "items": [
                    {
                        "topic": "#3dprinting",
                        "source": "instagram",
                        "views": 1200,
                        "likes": 80,
                        "comments": 5,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    batch = load_screening_export(export)

    assert batch.source_agent == "gen-forge-screening-agent"
    assert len(batch.items) == 1
    assert batch.items[0].topic == "#3dprinting"
