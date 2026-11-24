"""Campaign pipeline: generate brief and storyboard artifacts directly in workspace."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from genforge_marketing.intelligence.creative_generator import generate_original_reel
from genforge_marketing.intelligence.campaign_orchestrator import load_campaign

def build_campaign_creative(campaign_path: str | Path, duration_seconds: int = 20, brand_voice: str = "creative, helpful, maker-focused") -> dict[str, Any]:
    path=Path(campaign_path)
    if path.is_dir(): path=path/"campaign.json"
    campaign=load_campaign(path)
    root=path.parent
    brief_path=root/"drafts"/"creative-brief.json"
    storyboard_path=root/"production"/"storyboard.md"
    if brief_path.exists() or storyboard_path.exists():
        existing=[str(p.relative_to(root)) for p in (brief_path,storyboard_path) if p.exists()]
        raise FileExistsError("Refusing to overwrite existing campaign creative artifacts: "+", ".join(existing))
    brief=generate_original_reel(
        product_name=str(campaign.get("product","")).strip(),
        product_description=str(campaign.get("product_description","")),
        objective=str(campaign.get("objective","awareness")),
        audience=str(campaign.get("audience","people interested in custom 3D printed products")),
        platform=str(campaign.get("platform","Instagram Reels")),
        duration_seconds=duration_seconds,
        brand_voice=brand_voice,
    )
    scenes=brief["production_plan"]["scenes"]
    lines=["# Campaign Storyboard", "", f"**Campaign:** {campaign.get('campaign_name','')}","",
           f"**Product:** {campaign.get('product','')}","",f"**Duration:** {duration_seconds}s","",
           "| Scene | Time | Beat | Visual direction | Text/voice guidance | Edit notes |",
           "|---:|---|---|---|---|"]
    for s in scenes:
        lines.append(f"| {s['scene']} | {s['start_seconds']}–{s['end_seconds']}s | {s['phase']} | {s['visual_direction']} | {s['voiceover_or_text']} | {s['editing_notes']} |")
    lines.extend(["","## Shot list",""])
    lines.extend(f"- {shot}" for shot in brief["production_plan"]["shot_list"])
    lines.extend(["","## Audio direction",brief["production_plan"]["audio_direction"],"","## Caption draft",brief["production_plan"]["caption_draft"],"","## CTA options"])
    lines.extend(f"- {cta}" for cta in brief["production_plan"]["cta_options"])
    brief_path.parent.mkdir(parents=True,exist_ok=True)
    storyboard_path.parent.mkdir(parents=True,exist_ok=True)
    brief_path.write_text(json.dumps(brief,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    storyboard_path.write_text("\n".join(lines)+"\n",encoding="utf-8")
    manifest=json.loads(path.read_text(encoding="utf-8"))
    artifacts=manifest.setdefault("artifacts",{})
    artifacts.setdefault("brief",[]).append("drafts/creative-brief.json")
    artifacts.setdefault("storyboard",[]).append("production/storyboard.md")
    progress=manifest.setdefault("progress",{})
    progress["brief"]="in_progress"
    manifest.setdefault("stage_notes",{})["brief"]="Deterministic creative brief and storyboard generated; human review required."
    path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return {"campaign_name":campaign.get("campaign_name"),"brief_path":str(brief_path),"storyboard_path":str(storyboard_path),"scene_count":len(scenes),"duration_seconds":duration_seconds,"status":"draft_for_review","provider":"deterministic_local_template","model_used":None,"stage_status":"in_progress","files_created":[str(brief_path),str(storyboard_path)]}
