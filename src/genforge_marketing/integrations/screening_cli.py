"""JSON handoff adapter for the GenForge screening agent.

The first integration boundary is a versionable JSON export. The marketing
service does not import the screening agent's internals, so each repository
can evolve independently.
"""

import json
from pathlib import Path
from typing import Any

from genforge_marketing.models.opportunity import OpportunityBatch, TrendOpportunity


class ScreeningCLIError(RuntimeError):
    """Raised when screening output cannot be loaded or validated."""


def load_screening_export(path: Path) -> OpportunityBatch:
    """Load a JSON handoff file from the screening agent.

    Required shape:
      {"items": [{"topic": "#3dprinting", "source": "instagram"}]}

    Optional item fields include source_url, summary, views, likes, comments,
    relevance_score, observed_at, and raw.
    """
    try:
        payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        items = [TrendOpportunity.model_validate(item) for item in payload.get("items", [])]
        return OpportunityBatch(
            items=items,
            source_agent=payload.get("source_agent", "gen-forge-screening-agent"),
        )
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        raise ScreeningCLIError(f"Could not load screening export at {path}: {exc}") from exc
