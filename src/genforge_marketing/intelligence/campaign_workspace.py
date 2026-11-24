"""Create a structured, local campaign workspace with reusable manifests."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

def create_campaign_workspace(root: str | Path, campaign_name: str, product: str, objective: str = "awareness", platform: str = "Instagram Reels", audience: str = "") -> dict[str, Any]:
    workspace = Path(root) / _slug(campaign_name)
    folders = ("references", "observations", "drafts", "production", "published", "metrics", "experiments")
    for folder in folders:
        (workspace / folder).mkdir(parents=True, exist_ok=True)
    manifest = {"schema_version": 1, "campaign_id": _slug(campaign_name), "campaign_name": campaign_name, "product": product, "objective": objective, "platform": platform, "audience": audience, "status": "planning"}
    (workspace / "campaign.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    experiment = {"experiment_id": f"{_slug(campaign_name)}-experiment-01", "hypothesis": "", "variable_tested": "", "status": "planned", "variants": [{"name": "A", "creative_ids": []}, {"name": "B", "creative_ids": []}]}
    (workspace / "experiments" / "experiment-01.json").write_text(json.dumps(experiment, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    readme = "# " + campaign_name + "\n\nCampaign workspace for " + product + ".\n\n"
    readme += "Store reference material, observations, drafts, production assets, published records, metrics and experiments in their corresponding folders.\n"
    (workspace / "README.md").write_text(readme, encoding="utf-8")
    return {"workspace": str(workspace), "manifest": manifest, "folders": list(folders), "experiment_template": experiment}

def _slug(value: str) -> str:
    import re
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "campaign"
