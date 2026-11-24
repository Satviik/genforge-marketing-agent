"""Campaign workflow state and next-action planning."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

STAGES = [
    ("research", "Research and references"),
    ("analysis", "Creative analysis"),
    ("brief", "Creative brief"),
    ("storyboard", "Storyboard"),
    ("production", "Production"),
    ("review", "Human review"),
    ("published", "Published"),
    ("metrics", "Performance metrics"),
    ("learning", "Learning review"),
]

# Prerequisites must be completed or explicitly skipped before a stage can
# advance. Human approval remains an additional gate for publishing.
STAGE_PREREQUISITES = {
    "research": (),
    "analysis": ("research",),
    "brief": ("analysis",),
    "storyboard": ("brief",),
    "production": ("storyboard",),
    "review": ("production",),
    "published": ("review",),
    "metrics": ("published",),
    "learning": ("metrics",),
}

ADVANCING_STATUSES = {"in_progress", "completed", "approved", "skipped"}
SATISFIED_STATUSES = {"completed", "approved", "skipped"}

def load_campaign(path: str | Path) -> dict[str, Any]:
    campaign_path = Path(path)
    if campaign_path.is_dir():
        campaign_path = campaign_path / "campaign.json"
    data = json.loads(campaign_path.read_text(encoding="utf-8"))
    data["_campaign_file"] = str(campaign_path)
    return data

def status_report(campaign: dict[str, Any]) -> dict[str, Any]:
    progress = campaign.get("progress", {})
    rows = []
    next_stage = None
    for key, label in STAGES:
        status = progress.get(key, "pending")
        rows.append({"stage": key, "label": label, "status": status})
        if next_stage is None and status not in {"completed", "approved", "skipped"}:
            next_stage = key
    return {"campaign_id": campaign.get("campaign_id"), "campaign_name": campaign.get("campaign_name"), "status": campaign.get("status", "planning"), "stages": rows, "next_stage": next_stage, "human_approval_required_for": ["review", "published"], "automated_publishing": False}

def _validate_prerequisites(campaign: dict[str, Any], stage: str, status: str) -> None:
    if status not in ADVANCING_STATUSES:
        return
    progress = campaign.get("progress", {})
    missing = [
        prerequisite
        for prerequisite in STAGE_PREREQUISITES.get(stage, ())
        if progress.get(prerequisite, "pending") not in SATISFIED_STATUSES
    ]
    if missing:
        raise ValueError(
            f"Cannot set campaign stage '{stage}' to '{status}'; "
            f"prerequisite stage(s) not satisfied: {', '.join(missing)}."
        )

def update_stage(campaign_file: str | Path, stage: str, status: str, note: str = "") -> dict[str, Any]:
    if stage not in {key for key, _ in STAGES}:
        raise ValueError(f"Unknown campaign stage: {stage}")
    if status not in {"pending", "in_progress", "completed", "approved", "skipped", "blocked"}:
        raise ValueError(f"Invalid stage status: {status}")
    path = Path(campaign_file)
    campaign = load_campaign(path)
    _validate_prerequisites(campaign, stage, status)
    if stage == "published" and status in {"in_progress", "completed"}:
        review = campaign.get("review_record", {})
        if review.get("decision") != "approved" or campaign.get("status") != "approved_for_production":
            raise ValueError("Publishing is blocked until an explicit human review approval is recorded.")
    progress = campaign.setdefault("progress", {})
    progress[stage] = status
    if note:
        campaign.setdefault("stage_notes", {})[stage] = note
    campaign.pop("_campaign_file", None)
    path.write_text(json.dumps(campaign, indent=2, ensure_ascii=False), encoding="utf-8")
    return campaign
