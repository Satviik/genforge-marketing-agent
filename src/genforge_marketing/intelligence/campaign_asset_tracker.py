"""Asset registry and revision tracking for approved campaign production."""
from __future__ import annotations
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ASSET_STATES={"draft","review","approved","rejected"}

def _paths(campaign_path: str | Path):
    path=Path(campaign_path)
    if path.is_dir(): path=path/"campaign.json"
    campaign=json.loads(path.read_text(encoding="utf-8"))
    review=campaign.get("review_record",{})
    if campaign.get("status")!="approved_for_production" or review.get("decision")!="approved":
        raise ValueError("Asset management requires explicit campaign approval.")
    handoff=path.parent/"production"/"handoff"/"handoff.json"
    if not handoff.is_file(): raise ValueError("Asset management requires an existing production handoff.")
    return path.parent,handoff

def list_campaign_assets(campaign_path: str | Path) -> dict[str,Any]:
    root,manifest=_paths(campaign_path)
    data=json.loads(manifest.read_text(encoding="utf-8"))
    assets=data.setdefault("assets",[])
    return {"assets":assets,"count":len(assets),"manifest_path":str(manifest)}

def add_campaign_asset(campaign_path: str | Path, source: str | Path, name: str="", asset_type: str="other", notes: str="") -> dict[str,Any]:
    source=Path(source)
    if not source.is_file(): raise ValueError(f"Asset file not found: {source}")
    root,manifest=_paths(campaign_path)
    data=json.loads(manifest.read_text(encoding="utf-8")); assets=data.setdefault("assets",[])
    asset_id=f"asset-{len(assets)+1:03d}"
    safe_name=Path(name.strip() or source.name).name
    asset_dir=root/"production"/"assets"/asset_id
    asset_dir.mkdir(parents=True,exist_ok=True)
    dest=asset_dir/f"r001_{source.name}"
    shutil.copy2(source,dest)
    now=datetime.now(timezone.utc).isoformat()
    asset={"asset_id":asset_id,"name":safe_name,"type":asset_type.strip() or "other","status":"draft","notes":notes.strip(),"revision":1,"current_file":str(dest.relative_to(root)),"history":[{"revision":1,"file":str(dest.relative_to(root)),"created_at":now,"notes":"Initial asset"}],"created_at":now,"updated_at":now}
    assets.append(asset); manifest.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return asset

def revise_campaign_asset(campaign_path: str | Path, asset_id: str, source: str | Path, notes: str="") -> dict[str,Any]:
    source=Path(source)
    if not source.is_file(): raise ValueError(f"Revision file not found: {source}")
    root,manifest=_paths(campaign_path)
    data=json.loads(manifest.read_text(encoding="utf-8")); assets=data.setdefault("assets",[])
    asset=next((a for a in assets if a.get("asset_id")==asset_id),None)
    if asset is None: raise ValueError(f"Campaign asset not found: {asset_id}")
    rev=int(asset.get("revision",0))+1
    dest=root/"production"/"assets"/asset_id/f"r{rev:03d}_{source.name}"
    dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,dest)
    now=datetime.now(timezone.utc).isoformat(); rel=str(dest.relative_to(root))
    asset.update({"revision":rev,"current_file":rel,"updated_at":now,"status":"draft"})
    asset.setdefault("history",[]).append({"revision":rev,"file":rel,"created_at":now,"notes":notes.strip()})
    manifest.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return asset

def set_campaign_asset_status(campaign_path: str | Path, asset_id: str, status: str, notes: str="") -> dict[str,Any]:
    if status not in ASSET_STATES: raise ValueError(f"Asset status must be one of: {', '.join(sorted(ASSET_STATES))}")
    root,manifest=_paths(campaign_path)
    data=json.loads(manifest.read_text(encoding="utf-8")); assets=data.setdefault("assets",[])
    asset=next((a for a in assets if a.get("asset_id")==asset_id),None)
    if asset is None: raise ValueError(f"Campaign asset not found: {asset_id}")
    now=datetime.now(timezone.utc).isoformat()
    asset.update({"status":status,"updated_at":now})
    asset.setdefault("status_history",[]).append({"status":status,"updated_at":now,"notes":notes.strip()})
    manifest.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return asset
