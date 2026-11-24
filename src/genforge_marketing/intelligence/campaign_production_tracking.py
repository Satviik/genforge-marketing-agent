"""Track manually executed production stages for an approved campaign."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VALID_STATES={"not_started","in_progress","completed","blocked"}

def update_production_status(campaign_path: str | Path, status: str, notes: str = "") -> dict[str, Any]:
    if status not in VALID_STATES:
        raise ValueError(f"Status must be one of: {', '.join(sorted(VALID_STATES))}")
    path=Path(campaign_path)
    if path.is_dir(): path=path/"campaign.json"
    campaign=json.loads(path.read_text(encoding="utf-8"))
    review=campaign.get("review_record",{})
    if campaign.get("status")!="approved_for_production" or review.get("decision")!="approved":
        raise ValueError("Production tracking requires explicit campaign approval.")
    manifest_path=path.parent/"production"/"handoff"/"handoff.json"
    if not manifest_path.is_file():
        raise ValueError("Production tracking requires an existing handoff package.")
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    state=manifest.setdefault("production_tracking",{})
    now=datetime.now(timezone.utc).isoformat()
    state.update({"status":status,"updated_at":now,"notes":notes.strip()})
    if status=="in_progress":
        state.setdefault("started_at",now)
        manifest["production_started"]=True
    elif status=="completed":
        state.setdefault("started_at",now)
        state["completed_at"]=now
        manifest["production_started"]=True
    elif status=="not_started":
        state.pop("started_at",None)
        state.pop("completed_at",None)
        manifest["production_started"]=False
    elif status=="blocked":
        state.setdefault("started_at",now)
        manifest["production_started"]=True
    manifest["publishing_enabled"]=False
    manifest["note"]="Production status is manually tracked. Publishing is never enabled by this command."
    manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return {"status":status,"updated_at":now,"manifest_path":str(manifest_path),"production_started":manifest["production_started"],"publishing_enabled":False}
