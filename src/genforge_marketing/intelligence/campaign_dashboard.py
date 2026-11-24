"""Unified read-only campaign dashboard report."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from genforge_marketing.intelligence.campaign_execution_plan import campaign_plan
from genforge_marketing.intelligence.campaign_artifact_audit import audit_artifacts
from genforge_marketing.intelligence.campaign_quality_gate import quality_gate
from genforge_marketing.intelligence.campaign_orchestrator import load_campaign


def campaign_dashboard(campaign_path: str | Path) -> dict[str, Any]:
    path = Path(campaign_path)
    if path.is_dir():
        path = path / "campaign.json"
    campaign = load_campaign(path)
    plan = campaign_plan(path)
    audit = audit_artifacts(path)
    gate = quality_gate(path)

    blockers = []
    for item in audit["missing"]:
        blockers.append({
            "type": "missing_artifact",
            "stage": item["stage"],
            "path": item["path"],
            "reason": "Declared campaign artifact does not exist.",
            "suggested_action": f"Create {item['path']} for the {item['stage']} stage.",
        })
    review_items = [check for check in gate["checks"] if not check["passed"] and check.get("severity") == "warning"]
    for check in gate["checks"]:
        if not check["passed"] and check.get("severity", "error") == "error":
            blockers.append({
                "type": "quality_check",
                "stage": "review",
                "check": check["name"],
                "reason": check["detail"],
                "suggested_action": check["detail"],
            })

    if blockers:
        readiness = "blocked"
    elif gate["ready_for_human_review"]:
        readiness = "ready_for_human_review"
    else:
        readiness = "needs_review"

    handoff_dir = path.parent / "production" / "handoff"
    handoff_manifest = handoff_dir / "handoff.json"
    handoff_status = "created" if handoff_manifest.is_file() else "not_created"
    production_tracking = None
    production_tasks = []
    production_assets = []
    if handoff_manifest.is_file():
        try:
            handoff_data = __import__("json").loads(handoff_manifest.read_text(encoding="utf-8"))
            production_tracking = handoff_data.get("production_tracking", {"status": "not_started"})
            production_tasks = handoff_data.get("production_tasks", [])
            production_assets = handoff_data.get("assets", [])
        except (OSError, ValueError):
            production_tracking = {"status": "unknown", "error": "Handoff manifest could not be read."}

    return {
        "campaign_id": campaign.get("campaign_id"),
        "campaign_name": campaign.get("campaign_name"),
        "campaign_status": campaign.get("status", "planning"),
        "readiness": readiness,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "review_items": [{"check": item["name"], "reason": item["detail"], "required": True} for item in review_items],
        "next_stage": plan["next_stage"],
        "next_action": plan["next_action"],
        "stage_statuses": plan["stage_statuses"],
        "artifact_summary": {
            "checked": audit["checked_count"],
            "found": audit["existing_count"],
            "missing": audit["missing_count"],
            "missing_paths": [item["path"] for item in audit["missing"]],
        },
        "production_handoff": {
            "status": handoff_status,
            "manifest_path": str(handoff_manifest.relative_to(path.parent)),
            "production_started": False if handoff_status == "created" else None,
            "publishing_enabled": False,
            "tracking": production_tracking,
            "assets": {
                "count": len(production_assets),
                "draft": sum(1 for asset in production_assets if asset.get("status") == "draft"),
                "review": sum(1 for asset in production_assets if asset.get("status") == "review"),
                "approved": sum(1 for asset in production_assets if asset.get("status") == "approved"),
                "rejected": sum(1 for asset in production_assets if asset.get("status") == "rejected"),
                "revisions": sum(int(asset.get("revision", 1)) for asset in production_assets),
            },
            "tasks": {
                "count": len(production_tasks),
                "completed": sum(1 for task in production_tasks if task.get("status") == "completed"),
                "in_progress": sum(1 for task in production_tasks if task.get("status") == "in_progress"),
                "blocked": sum(1 for task in production_tasks if task.get("status") == "blocked"),
                "todo": sum(1 for task in production_tasks if task.get("status") == "todo"),
            },
        },
        "quality_summary": {
            "passed": gate["passed"],
            "failed": gate["failed"],
            "ready_for_human_review": gate["ready_for_human_review"],
            "approval_required": gate["approval_required"],
        },
        "human_approval_required": True,
        "automated_publishing": False,
        "recommendation": "Resolve listed blockers, complete the current stage, then review the campaign manually.",
        "read_only": True,
    }
