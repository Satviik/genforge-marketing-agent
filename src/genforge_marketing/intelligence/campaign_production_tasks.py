"""Task management for campaign production handoffs."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TASK_STATES={"todo","in_progress","completed","blocked"}
PRIORITIES={"low","medium","high"}

def _manifest(campaign_path: str | Path) -> Path:
    path=Path(campaign_path)
    if path.is_dir(): path=path/"campaign.json"
    campaign=json.loads(path.read_text(encoding="utf-8"))
    if campaign.get("status")!="approved_for_production" or campaign.get("review_record",{}).get("decision")!="approved":
        raise ValueError("Production tasks require explicit campaign approval.")
    manifest=path.parent/"production"/"handoff"/"handoff.json"
    if not manifest.is_file(): raise ValueError("Production task management requires an existing handoff.")
    return manifest

def list_production_tasks(campaign_path: str | Path) -> dict[str, Any]:
    manifest_path=_manifest(campaign_path)
    data=json.loads(manifest_path.read_text(encoding="utf-8"))
    tasks=data.setdefault("production_tasks",[])
    return {"tasks":tasks,"count":len(tasks),"manifest_path":str(manifest_path)}

def add_production_task(campaign_path: str | Path, title: str, description: str="", assignee: str="", priority: str="medium", due_date: str="") -> dict[str, Any]:
    title=title.strip()
    if not title: raise ValueError("Task title is required.")
    if priority not in PRIORITIES: raise ValueError(f"Priority must be one of: {', '.join(sorted(PRIORITIES))}")
    if due_date:
        try: datetime.strptime(due_date,"%Y-%m-%d")
        except ValueError as exc: raise ValueError("Due date must use YYYY-MM-DD.") from exc
    path=_manifest(campaign_path); data=json.loads(path.read_text(encoding="utf-8")); tasks=data.setdefault("production_tasks",[])
    task={"task_id":f"task-{len(tasks)+1:03d}","title":title,"description":description.strip(),"assignee":assignee.strip(),"priority":priority,"due_date":due_date,"status":"todo","created_at":datetime.now(timezone.utc).isoformat(),"updated_at":datetime.now(timezone.utc).isoformat()}
    tasks.append(task); path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return task

def update_production_task(campaign_path: str | Path, task_id: str, status: str, notes: str="") -> dict[str, Any]:
    if status not in TASK_STATES: raise ValueError(f"Status must be one of: {', '.join(sorted(TASK_STATES))}")
    path=_manifest(campaign_path); data=json.loads(path.read_text(encoding="utf-8")); tasks=data.setdefault("production_tasks",[])
    task=next((item for item in tasks if item.get("task_id")==task_id),None)
    if task is None: raise ValueError(f"Production task not found: {task_id}")
    task.update({"status":status,"updated_at":datetime.now(timezone.utc).isoformat()})
    if notes.strip(): task["notes"]=notes.strip()
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return task
