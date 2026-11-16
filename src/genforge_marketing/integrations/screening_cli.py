"""Subprocess adapter for the existing GenForge screening CLI.

The marketing agent consumes a stable JSON export instead of importing the
screening agent's internal Python modules. This keeps the repositories decoupled.
"""

import json
import subprocess
from pathlib import Path
from typing import Any

from genforge_marketing.models.opportunity import OpportunityBatch, TrendOpportunity


class ScreeningCLIError(RuntimeError):
    """Raised when the screening CLI cannot provide valid output."""


def _parse_export(payload: dict[str, Any]) -> OpportunityBatch:
    items = [TrendOpportunity.model_validate(item) for item in payload.get("items", [])]
    return OpportunityBatch(
        items=items,
        source_agent=payload.get("source_agent", "gen-forge-screening-agent"),
    )


def load_screening_export(path: Path) -> OpportunityBatch:
    """Load a JSON export produced by the screening agent."""
    try:
        payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return _parse_export(payload)
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        raise ScreeningCLIError(f"Could not load screening export at {path}: {exc}") from exc


def run_screening_export(
    command: str = "genforge",
    timeout_seconds: int = 120,
    limit: int = 200,
) -> OpportunityBatch:
    """Execute 'genforge export' and parse its JSON stdout."""
    try:
        completed = subprocess.run(
            [command, "export", "--output", "-", "--limit", str(limit)],
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        payload: dict[str, Any] = json.loads(completed.stdout)
        return _parse_export(payload)
    except FileNotFoundError as exc:
        raise ScreeningCLIError(f"Screening CLI executable not found: {command}") from exc
    except subprocess.TimeoutExpired as exc:
        raise ScreeningCLIError(f"Screening CLI timed out after {timeout_seconds}s") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or str(exc)
        raise ScreeningCLIError(f"Screening CLI failed: {detail}") from exc
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        raise ScreeningCLIError(f"Screening CLI returned invalid JSON: {exc}") from exc
