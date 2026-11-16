"""MCP server exposing GenForge marketing planning tools to Claude.

Run with `genforge-marketing-mcp`. The server uses stdio transport so it can
be registered as a local MCP server in Claude Desktop/Claude Code.
"""

import json
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from genforge_marketing.config import get_settings
from genforge_marketing.planning.generator import generate_monthly_plan
from genforge_marketing.planning.models import MonthlyContentPlan
from genforge_marketing.planning.occasions import OccasionCalendar
from genforge_marketing.profile.models import BusinessProfile
from genforge_marketing.workbook.exporter import export_monthly_plan

server = FastMCP(
    "GenForge Marketing",
    instructions=(
        "Plan GenForge Instagram content only when requested. Use supplied "
        "business facts and occasion evidence. Clearly distinguish verified "
        "festivals from suggestions. Plans are drafts; this server does not "
        "approve or publish content. Never claim that a post was published."
    ),
)


def _json_error(error: Exception) -> str:
    return json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False)


@server.tool()
def get_marketing_capabilities() -> str:
    """Describe available GenForge planning tools and their safety boundaries."""
    return json.dumps(
        {
            "ok": True,
            "server": "GenForge Marketing",
            "capabilities": [
                "load_business_profile",
                "generate_monthly_content_plan",
                "export_content_plan_workbook",
            ],
            "planning_mode": "on_demand",
            "workbook_sheets": ["Posts", "Reels"],
            "publishing_enabled": False,
            "approval_required_before_publishing": True,
            "festival_dates_are_never_guessed": True,
        },
        ensure_ascii=False,
    )


@server.tool()
def load_business_profile(profile_path: str = "genforge-business.json") -> str:
    """Load and validate GenForge's business profile from a local JSON file."""
    try:
        path = Path(profile_path).expanduser().resolve()
        if not path.is_file():
            return _json_error(FileNotFoundError(f"Profile file not found: {path}"))
        profile = BusinessProfile.model_validate_json(path.read_text(encoding="utf-8"))
        return json.dumps(
            {
                "ok": True,
                "profile_path": str(path),
                "profile": profile.model_dump(mode="json"),
                "available_products": [
                    product.name for product in profile.products if product.available
                ],
            },
            ensure_ascii=False,
        )
    except (OSError, ValidationError, ValueError) as exc:
        return _json_error(exc)


@server.tool()
def generate_monthly_content_plan(
    profile_json: str,
    year: int,
    month: int,
    posts: int = 8,
    reels: int = 8,
    post_time: str = "19:00",
    reel_time: str = "18:30",
    occasion_calendar_json: str = "",
) -> str:
    """Generate an on-demand draft plan. Pass optional researched occasions as JSON.

    The occasion JSON must contain year, month, market and occasions. Each
    verified occasion must include source_name or source_url. Suggested
    occasions remain marked as suggestions. This tool does not publish.
    """
    from datetime import time

    try:
        profile = BusinessProfile.model_validate_json(profile_json)
        occasion_calendar = (
            OccasionCalendar.model_validate_json(occasion_calendar_json)
            if occasion_calendar_json.strip()
            else None
        )
        plan = generate_monthly_plan(
            profile=profile,
            year=year,
            month=month,
            post_count=posts,
            reel_count=reels,
            post_time=time.fromisoformat(post_time),
            reel_time=time.fromisoformat(reel_time),
            occasion_calendar=occasion_calendar,
        )
        return json.dumps(
            {
                "ok": True,
                "status": "draft",
                "plan": plan.model_dump(mode="json"),
                "occasion_count": len(plan.occasions),
                "verified_occasions": [
                    item.name for item in plan.occasions
                    if item.confidence.value == "verified"
                ],
                "suggested_occasions": [
                    item.name for item in plan.occasions
                    if item.confidence.value == "suggested"
                ],
                "next_step": "Review the draft and export the workbook. Nothing is approved or published.",
            },
            ensure_ascii=False,
        )
    except (ValidationError, ValueError, OSError) as exc:
        return _json_error(exc)


@server.tool()
def export_content_plan_workbook(plan_json: str, filename: str = "content-plan.xlsx") -> str:
    """Export a validated monthly plan to an Excel workbook with Posts and Reels sheets.

    The filename must be a simple .xlsx filename. Files are written only under
    the configured GenForge data directory's plans subfolder.
    """
    try:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}\.xlsx", filename):
            return _json_error(ValueError("filename must be a simple .xlsx filename"))
        plan = MonthlyContentPlan.model_validate_json(plan_json)
        destination = (get_settings().data_dir / "plans" / filename).resolve()
        allowed_root = (get_settings().data_dir / "plans").resolve()
        if destination.parent != allowed_root:
            return _json_error(ValueError("Invalid workbook destination"))
        export_monthly_plan(plan, destination)
        return json.dumps(
            {
                "ok": True,
                "workbook_path": str(destination),
                "worksheets": ["Posts", "Reels"],
                "status": "draft",
                "message": "Workbook exported. Content remains unapproved and unpublished.",
            },
            ensure_ascii=False,
        )
    except (ValidationError, ValueError, OSError) as exc:
        return _json_error(exc)


def main() -> None:
    """Start the MCP server over stdio."""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
