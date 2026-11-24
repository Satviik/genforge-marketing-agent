"""Record explicit human campaign decisions with a review audit trail."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any

from genforge_marketing.intelligence.campaign_orchestrator import load_campaign
from genforge_marketing.intelligence.campaign_quality_gate import quality_gate

DECISIONS = {"approved", "changes_requested", "rejected"}

def record_campaign_review(campaign_path: str | Path, reviewer: str, decision: str, notes: str = "") -> dict[str, Any]:
    if decision not in DECISIONS:
        raise ValueError(f"Decision must be one of: {', '.join(sorted(DECISIONS))}")
    reviewer = reviewer.strip()
    if not reviewer:
        raise ValueError("Reviewer name is required.")
    path = Path(campaign_path)
    if path.is_dir():
        path = path / "campaign.json"
    campaign = load_campaign(path)
    if decision == "approved":
        gate = quality_gate(path)
        if not gate["ready_for_human_review"]:
            raise ValueError("Cannot approve: campaign is not ready for human review. Resolve critical blockers first.")
    progress = campaign.setdefault("progress", {})
    progress["review"] = {"approved": "approved", "changes_requested": "in_progress", "rejected": "blocked"}[decision]
    record = {"reviewer": reviewer, "decision": decision, "notes": notes.strip(), "reviewed_at": datetime.now(timezone.utc).isoformat()}
    campaign["review_record"] = record
    if decision == "approved":
        campaign["status"] = "approved_for_production"
    elif decision == "rejected":
        campaign["status"] = "rejected"
    else:
        campaign["status"] = "needs_changes"
    campaign.pop("_campaign_file", None)
    path.write_text(json.dumps(campaign, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return record
