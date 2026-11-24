"""Create non-destructive starter task files for a campaign's next stage."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from genforge_marketing.intelligence.campaign_execution_plan import campaign_plan

TASK_FILES = {
 "research": ("observations/research-notes.md", "# Research notes\n\n## Product context\n\n## Audience questions\n\n## Trends and references\n\n## Evidence and source dates\n\n## Findings\n"),
 "analysis": ("observations/creative-analysis.md", "# Creative analysis\n\n## Reference inventory\n\n## Hook\n\n## Scene and pacing notes\n\n## Payoff and CTA\n\n## Originality/adaptation notes\n"),
 "brief": ("drafts/creative-brief.md", "# Creative brief\n\n## Objective\n\n## Audience\n\n## Core message\n\n## Hook\n\n## Proof / process\n\n## Payoff\n\n## CTA\n\n## Originality guardrails\n"),
 "storyboard": ("production/storyboard.md", "# Storyboard\n\n| Time | Scene | Visual | On-screen text | Audio |\n|---|---|---|---|---|\n| | | | |\n"),
 "production": ("production/production-checklist.md", "# Production checklist\n\n- [ ] Assets prepared\n- [ ] Video assembled\n- [ ] Audio rights checked\n- [ ] Captions reviewed\n- [ ] Draft export saved\n"),
 "review": ("drafts/review-checklist.md", "# Human review\n\n- [ ] Accurate\n- [ ] Original\n- [ ] Brand fit\n- [ ] Rights cleared\n- [ ] Accessibility/captions\n- [ ] Approved by human\n\nReviewer: \nDate: \nDecision: pending\n"),
 "published": ("published/publishing-record.md", "# Publishing record\n\nPlatform: \nURL: \nPublish date/time: \nCreative ID: \n"),
 "metrics": ("metrics/metrics-template.json", "{\n  \"observed_at\": \"\",\n  \"platform\": \"\",\n  \"views\": null,\n  \"reach\": null,\n  \"watch_time_seconds\": null,\n  \"likes\": null,\n  \"comments\": null,\n  \"shares\": null,\n  \"saves\": null,\n  \"profile_visits\": null,\n  \"inquiries\": null,\n  \"orders\": null,\n  \"revenue_inr\": null\n}\n"),
 "learning": ("experiments/learning-review.md", "# Learning review\n\n## Observed results\n\n## Patterns (descriptive only)\n\n## What remains uncertain\n\n## Next experiment\n")
}
def create_stage_task(campaign_path: str | Path, stage: str | None = None) -> dict[str, Any]:
 path=Path(campaign_path)
 if path.is_dir(): path=path/"campaign.json"
 root=path.parent
 plan=campaign_plan(path)
 selected=stage or plan["next_stage"]
 if not selected: raise ValueError("Campaign has no pending stage.")
 if selected not in TASK_FILES: raise ValueError(f"Unknown campaign stage: {selected}")
 rel,template=TASK_FILES[selected]
 target=root/rel
 if target.exists(): raise FileExistsError(f"Task file already exists; refusing to overwrite: {target}")
 target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(template,encoding="utf-8")
 return {"stage":selected,"path":str(target),"created":True,"campaign_name":plan["campaign_name"],"note":"Starter only. Campaign stage status was not changed."}
