"""Audit campaign deliverables declared in the campaign manifest."""
from __future__ import annotations
from pathlib import Path
from typing import Any

def audit_artifacts(campaign_file: str | Path) -> dict[str, Any]:
    path = Path(campaign_file)
    if path.is_dir():
        path = path / "campaign.json"
    root = path.parent
    import json
    campaign = json.loads(path.read_text(encoding="utf-8"))
    declared = campaign.get("artifacts", {})
    checks = []
    for stage, items in declared.items():
        if not isinstance(items, list):
            items = [items]
        for item in items:
            rel = str(item)
            target = root / rel
            checks.append({"stage": stage, "path": rel, "exists": target.exists(), "is_file": target.is_file()})
    missing = [c for c in checks if not c["exists"]]
    return {"campaign_id": campaign.get("campaign_id"), "campaign_name": campaign.get("campaign_name"),
            "checked_count": len(checks), "existing_count": len(checks)-len(missing), "missing_count": len(missing),
            "checks": checks, "missing": missing,
            "note": "Only manifest-declared artifacts are checked. This audit does not automatically mark stages complete."}
