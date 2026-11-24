"""Create a gated production handoff from an explicitly approved campaign."""
from __future__ import annotations
import json
import shutil
from pathlib import Path
from typing import Any

def create_production_handoff(campaign_path: str | Path) -> dict[str, Any]:
    path=Path(campaign_path)
    if path.is_dir(): path=path/"campaign.json"
    root=path.parent
    campaign=json.loads(path.read_text(encoding="utf-8"))
    review=campaign.get("review_record",{})
    if campaign.get("status")!="approved_for_production" or campaign.get("progress",{}).get("review")!="approved" or review.get("decision")!="approved":
        raise ValueError("Production handoff requires an explicit recorded approval.")
    brief=root/"drafts"/"creative-brief.json"
    storyboard=root/"production"/"storyboard.md"
    if not brief.is_file() or not storyboard.is_file():
        raise ValueError("Production handoff requires the creative brief JSON and storyboard Markdown.")
    handoff=root/"production"/"handoff"
    handoff.mkdir(parents=True,exist_ok=True)
    shutil.copy2(brief,handoff/"creative-brief.json")
    shutil.copy2(storyboard,handoff/"storyboard.md")
    checklist=handoff/"production-checklist.md"
    if not checklist.exists():
        checklist.write_text("# Production handoff checklist\n\n- [ ] Confirm product details and measurements\n- [ ] Gather approved physical product and props\n- [ ] Record footage according to storyboard\n- [ ] Edit and add captions\n- [ ] Check audio rights and brand accuracy\n- [ ] Export draft for final review\n- [ ] Obtain final human approval before publishing\n",encoding="utf-8")
    manifest={"campaign_id":campaign.get("campaign_id"),"campaign_name":campaign.get("campaign_name"),"approval":review,"source_files":["drafts/creative-brief.json","production/storyboard.md"],"handoff_files":["production/handoff/creative-brief.json","production/handoff/storyboard.md","production/handoff/production-checklist.md"],"production_started":False,"publishing_enabled":False,"note":"Handoff package only. Production and publishing remain manual."}
    out=handoff/"handoff.json"
    out.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return {"campaign_name":campaign.get("campaign_name"),"handoff_dir":str(handoff),"manifest_path":str(out),"files":manifest["handoff_files"],"production_started":False,"publishing_enabled":False}
