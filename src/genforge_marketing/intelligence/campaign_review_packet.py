"""Export an editable campaign review packet without changing campaign state."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from genforge_marketing.intelligence.campaign_dashboard import campaign_dashboard


def build_campaign_review_packet(campaign_path: str | Path) -> dict[str, Any]:
    path = Path(campaign_path)
    if path.is_dir():
        path = path / "campaign.json"
    root = path.parent
    campaign = json.loads(path.read_text(encoding="utf-8"))
    dashboard = campaign_dashboard(path)
    brief_path = root / "drafts" / "creative-brief.json"
    storyboard_path = root / "production" / "storyboard.md"
    brief = json.loads(brief_path.read_text(encoding="utf-8")) if brief_path.exists() else None
    storyboard = storyboard_path.read_text(encoding="utf-8") if storyboard_path.exists() else None

    lines = [
        f"# Campaign Review Packet: {campaign.get('campaign_name', 'Untitled')}",
        "",
        "## Campaign summary",
        f"- Product: {campaign.get('product', 'Not specified')}",
        f"- Objective: {campaign.get('objective', 'Not specified')}",
        f"- Platform: {campaign.get('platform', 'Not specified')}",
        f"- Audience: {campaign.get('audience', 'Not specified')}",
        f"- Status: {dashboard['campaign_status']}",
        f"- Readiness: {dashboard['readiness']}",
        f"- Blockers: {dashboard['blocker_count']}",
        "",
        "## Review guidance",
        "This packet is a draft for human review. Readiness is not approval. Publishing is disabled.",
        "",
        "## Blockers",
    ]
    if dashboard["blockers"]:
        for item in dashboard["blockers"]:
            location = item.get("path") or item.get("check") or item.get("stage", "Campaign")
            lines.append(f"- **{location}** — {item['reason']} Action: {item['suggested_action']}")
    else:
        lines.append("- No content blockers reported by the current dashboard.")
    lines.extend(["", "## Human review items"])
    if dashboard["review_items"]:
        for item in dashboard["review_items"]:
            lines.append(f"- [ ] **{item['check']}** — {item['reason']}")
    else:
        lines.append("- [ ] Review content, brand accuracy, claims, and final edit.")
    lines.extend(["", "## Creative brief"])
    if brief is not None:
        lines.append("~~~json")
        lines.append(json.dumps(brief, indent=2, ensure_ascii=False))
        lines.append("~~~")
    else:
        lines.append("No creative brief found.")
    lines.extend(["", "## Storyboard"])
    lines.append(storyboard if storyboard is not None else "No storyboard found.")
    lines.extend([
        "",
        "## Human decision",
        "- [ ] Approved for production",
        "- [ ] Needs changes",
        "- [ ] Rejected",
        "",
        "Reviewer: ____________________",
        "Date: ____________________",
        "Notes:",
        "",
        "## Production / publishing reminder",
        "Approval must be recorded in the campaign workspace before any publishing step. This packet does not approve or publish content.",
        "",
    ])
    return {
        "campaign_name": campaign.get("campaign_name"),
        "readiness": dashboard["readiness"],
        "blocker_count": dashboard["blocker_count"],
        "markdown": "\n".join(lines),
        "read_only": True,
        "approval_required": True,
        "publishing_enabled": False,
    }


def export_campaign_review_packet(campaign_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    packet = build_campaign_review_packet(campaign_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(packet["markdown"], encoding="utf-8")
    return {**{k: v for k, v in packet.items() if k != "markdown"}, "output_path": str(output)}
