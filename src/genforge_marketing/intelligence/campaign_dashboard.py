"""Unified read-only campaign dashboard report."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from genforge_marketing.intelligence.campaign_execution_plan import campaign_plan
from genforge_marketing.intelligence.campaign_artifact_audit import audit_artifacts
from genforge_marketing.intelligence.campaign_quality_gate import quality_gate
from genforge_marketing.intelligence.campaign_orchestrator import load_campaign

def campaign_dashboard(campaign_path: str | Path) -> dict[str, Any]:
 path=Path(campaign_path)
 if path.is_dir(): path=path/"campaign.json"
 campaign=load_campaign(path)
 plan=campaign_plan(path)
 audit=audit_artifacts(path)
 gate=quality_gate(path)
 return {
  "campaign_id":campaign.get("campaign_id"),
  "campaign_name":campaign.get("campaign_name"),
  "campaign_status":campaign.get("status","planning"),
  "next_stage":plan["next_stage"],
  "next_action":plan["next_action"],
  "stage_statuses":plan["stage_statuses"],
  "artifact_summary":{"checked":audit["checked_count"],"found":audit["existing_count"],"missing":audit["missing_count"],"missing_paths":[item["path"] for item in audit["missing"]]},
  "quality_summary":{"passed":gate["passed"],"failed":gate["failed"],"ready_for_human_review":gate["ready_for_human_review"],"approval_required":gate["approval_required"]},
  "human_approval_required":True,
  "automated_publishing":False,
  "recommendation":"Review missing artifacts and failed quality checks, then complete the current stage manually.",
  "read_only":True
 }
