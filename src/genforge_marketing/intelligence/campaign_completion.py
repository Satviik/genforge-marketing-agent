"""Final campaign completion audit and report."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from genforge_marketing.intelligence.campaign_orchestrator import load_campaign, STAGES

REQUIRED_FINAL_STAGES=("published","metrics","learning")

def campaign_completion_report(campaign_path: str | Path) -> dict[str,Any]:
    path=Path(campaign_path)
    if path.is_dir(): path=path/"campaign.json"
    campaign=load_campaign(path)
    progress=campaign.get("progress",{})
    review=campaign.get("review_record",{})
    issues=[]
    if review.get("decision")!="approved":
        issues.append({"code":"human_review_missing","message":"Campaign does not have an explicit human approval record."})
    if campaign.get("status")!="approved_for_production":
        issues.append({"code":"campaign_not_approved","message":"Campaign status is not approved_for_production."})
    for stage in REQUIRED_FINAL_STAGES:
        if progress.get(stage)!="completed":
            issues.append({"code":"stage_incomplete","stage":stage,"message":f"Stage '{stage}' is not completed."})
    handoff=path.parent/"production"/"handoff"/"handoff.json"
    tasks=[];assets=[]
    if not handoff.is_file():
        issues.append({"code":"handoff_missing","message":"Production handoff manifest is missing."})
    else:
        try:
            data=json.loads(handoff.read_text(encoding="utf-8"))
            tasks=data.get("production_tasks",[]); assets=data.get("assets",[])
            for task in tasks:
                if task.get("status")!="completed":
                    issues.append({"code":"task_incomplete","task_id":task.get("task_id"),"message":f"Production task '{task.get('title','(untitled)')}' is not completed."})
            for asset in assets:
                if asset.get("status")!="approved":
                    issues.append({"code":"asset_unapproved","asset_id":asset.get("asset_id"),"message":f"Asset '{asset.get('name','(unnamed)')}' is not approved."})
        except (OSError,ValueError) as exc:
            issues.append({"code":"handoff_unreadable","message":f"Production handoff cannot be read: {exc}"})
    complete=not issues
    return {"campaign_id":campaign.get("campaign_id"),"campaign_name":campaign.get("campaign_name"),"complete":complete,"status":"completed" if complete else "incomplete","issue_count":len(issues),"issues":issues,"summary":{"required_final_stages":list(REQUIRED_FINAL_STAGES),"completed_final_stages":[s for s in REQUIRED_FINAL_STAGES if progress.get(s)=="completed"],"production_tasks":len(tasks),"completed_tasks":sum(1 for t in tasks if t.get("status")=="completed"),"assets":len(assets),"approved_assets":sum(1 for a in assets if a.get("status")=="approved")},"human_approval_required":True,"automated_publishing":False,"read_only":True}
