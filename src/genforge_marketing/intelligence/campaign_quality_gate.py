"""Quality gate checks for campaign creative artifacts. Local, deterministic, advisory."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

def _check(name: str, ok: bool, detail: str, severity: str="error") -> dict[str,Any]:
 return {"name":name,"passed":bool(ok),"severity":severity,"detail":detail}

def quality_gate(campaign_path: str | Path) -> dict[str,Any]:
 path=Path(campaign_path)
 if path.is_dir(): path=path/"campaign.json"
 root=path.parent
 campaign=json.loads(path.read_text(encoding="utf-8"))
 checks=[]
 brief_path=root/"drafts"/"creative-brief.json"
 storyboard_path=root/"production"/"storyboard.md"
 brief=None
 if brief_path.exists():
  try: brief=json.loads(brief_path.read_text(encoding="utf-8"))
  except json.JSONDecodeError: checks.append(_check("brief_json_valid",False,"Brief file is not valid JSON."))
 else: checks.append(_check("brief_exists",False,"Creative brief file is missing."))
 if brief is not None:
  checks.append(_check("brief_json_valid",True,"Brief JSON parses."))
  product=brief.get("product",{})
  checks.append(_check("product_name",bool(product.get("name")),"Product name is present." if product.get("name") else "Product name is missing."))
  concept=brief.get("creative_concept",{})
  checks.append(_check("creative_concept",bool(concept.get("core_idea")),"Core creative idea present." if concept.get("core_idea") else "Core creative idea missing."))
  hooks=concept.get("hook_options",[])
  checks.append(_check("hook_options",isinstance(hooks,list) and len(hooks)>=2,"At least two hook options are required." if isinstance(hooks,list) and len(hooks)>=2 else "Add at least two hook options."))
  plan=brief.get("production_plan",{})
  scenes=plan.get("scenes",[])
  valid_scenes=isinstance(scenes,list) and len(scenes)>=3 and all(isinstance(s,dict) and s.get("visual_direction") and s.get("voiceover_or_text") and isinstance(s.get("start_seconds"),int) and isinstance(s.get("end_seconds"),int) and s["end_seconds"]>s["start_seconds"] for s in scenes)
  checks.append(_check("scene_structure",valid_scenes,"Scenes have timing, visual direction and text/audio guidance." if valid_scenes else "Scenes must include valid positive timing, visual direction and text/audio guidance."))
  duration=brief.get("campaign",{}).get("duration_seconds")
  timeline_valid=valid_scenes and isinstance(duration,int) and scenes[0]["start_seconds"]==0 and scenes[-1]["end_seconds"]==duration and all(scenes[i]["end_seconds"]==scenes[i+1]["start_seconds"] for i in range(len(scenes)-1))
  checks.append(_check("timeline_contiguous",timeline_valid,"Scene timings cover the brief duration without gaps or overlaps." if timeline_valid else "Scene timing must start at zero, be contiguous and end at the declared duration."))
  cta=plan.get("cta_options",[])
  checks.append(_check("cta_present",isinstance(cta,list) and bool(cta),"CTA options exist." if isinstance(cta,list) and cta else "Add at least one CTA."))
 if storyboard_path.exists():
  content=storyboard_path.read_text(encoding="utf-8")
  checks.append(_check("storyboard_exists",True,"Storyboard file exists."))
  checks.append(_check("storyboard_content",len(content.strip())>100 and "| Scene |" in content,"Storyboard contains scene table." if len(content.strip())>100 and "| Scene |" in content else "Storyboard needs a scene table and meaningful content."))
 else: checks.append(_check("storyboard_exists",False,"Storyboard file is missing."))
 artifacts=campaign.get("artifacts",{})
 declared=[str(item) for group in artifacts.values() for item in (group if isinstance(group,list) else [group])]
 missing=[p for p in declared if not (root/Path(p)).exists()]
 checks.append(_check("declared_artifacts",not missing,"All declared artifacts exist." if not missing else "Missing declared artifacts: "+", ".join(missing)))
 checks.append(_check("human_review_recorded",campaign.get("progress",{}).get("review") in {"approved","completed"},"Human review recorded." if campaign.get("progress",{}).get("review") in {"approved","completed"} else "Human review is pending; gate remains advisory."))
 passed=sum(1 for c in checks if c["passed"])
 return {"campaign_name":campaign.get("campaign_name"),"campaign_id":campaign.get("campaign_id"),"passed":passed,"failed":len(checks)-passed,"checks":checks,"ready_for_human_review":all(c["passed"] for c in checks if c["severity"]=="error"),"approval_required":True,"automated_publish_allowed":False,"note":"Quality checks are deterministic and advisory. Passing is not approval to publish."}
