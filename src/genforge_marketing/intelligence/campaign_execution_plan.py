"""Deterministic campaign execution planner: proposes next action without side effects."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from genforge_marketing.intelligence.campaign_orchestrator import load_campaign, status_report
from genforge_marketing.intelligence.campaign_artifact_audit import audit_artifacts

STAGE_GUIDANCE = {
    "research": "Collect product context, audience questions, reference links and trend evidence in references/ and observations/. Record sources and dates.",
    "analysis": "Run Reel autopsy and timeline reconstruction on selected references. Save the observations; do not copy reference scripts or shots.",
    "brief": "Create an original creative brief with objective, audience, core message, hook, proof, payoff, CTA and originality notes.",
    "storyboard": "Turn the approved brief into a timed scene plan and storyboard. Verify every scene has a visual, on-screen text and audio/narration direction.",
    "production": "Produce the creative from the storyboard. Save draft exports and production assets; do not publish.",
    "review": "Review factual accuracy, originality, brand fit, rights, accessibility and safety. Human approval is required.",
    "published": "After approval, publish manually and record the post URL, publish timestamp and platform in published/.",
    "metrics": "Record a dated performance snapshot in metrics/ using comparable observation windows.",
    "learning": "Summarize observed metrics and tagged patterns. Treat findings as hypotheses, not causal claims; define the next experiment.",
}
def campaign_plan(path: str | Path) -> dict[str, Any]:
    campaign = load_campaign(path)
    report = status_report(campaign)
    next_stage = report["next_stage"]
    audit = audit_artifacts(path)
    if next_stage is None:
        action = "Review campaign history and define the next experiment."
        stage = None
        blocking = []
    else:
        stage = next_stage
        action = STAGE_GUIDANCE[stage]
        blocking = [x for x in audit["missing"] if x["stage"] == stage]
        if campaign.get("progress", {}).get(stage) == "blocked":
            action = "Resolve the stage blocker recorded in stage_notes, then update the stage status."
    return {
        "campaign_id": report["campaign_id"],
        "campaign_name": report["campaign_name"],
        "campaign_status": report["status"],
        "next_stage": stage,
        "next_action": action,
        "missing_artifacts_for_next_stage": blocking,
        "missing_artifact_count": audit["missing_count"],
        "approval_required": stage in {"review", "published"},
        "automated_side_effects": False,
        "stage_statuses": report["stages"],
        "notes": ["This is a deterministic planning suggestion.", "It does not create files, run external services, change stage statuses, or publish content."]
    }
