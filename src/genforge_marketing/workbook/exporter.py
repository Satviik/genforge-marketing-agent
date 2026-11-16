"""Create the two-sheet monthly content planning workbook."""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from genforge_marketing.planning.models import MonthlyContentPlan


POST_COLUMNS = [
    "content_id", "planned_date", "planned_time", "platform", "post_type", "product",
    "campaign", "objective", "audience", "creative_brief", "caption", "hashtags", "cta",
    "asset_path", "approval_status", "publishing_status", "published_url", "reach",
    "impressions", "likes", "comments", "saves", "shares", "profile_visits", "notes",
]
REEL_COLUMNS = [
    "content_id", "planned_date", "planned_time", "platform", "product", "campaign",
    "objective", "audience", "reel_format", "hook", "scene_plan", "script",
    "on_screen_text", "voiceover", "audio_direction", "caption", "hashtags", "cta",
    "asset_path", "approval_status", "publishing_status", "published_url", "views",
    "reach", "watch_time_seconds", "average_watch_time_seconds", "likes", "comments",
    "saves", "shares", "profile_visits", "notes",
]


def _row(item, columns: list[str]) -> list[object]:
    values = item.model_dump(mode="json")
    values["hashtags"] = " ".join(values.get("hashtags", []))
    return [values.get(column, "") if values.get(column) is not None else "" for column in columns]


def _populate(sheet, columns: list[str], items: list, tab_color: str) -> None:
    sheet.append(columns)
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = f"A1:{get_column_letter(len(columns))}1"
    sheet.sheet_view.showGridLines = False
    sheet.sheet_properties.tabColor = tab_color
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="252A34")
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    sheet.row_dimensions[1].height = 32
    for item in items:
        sheet.append(_row(item, columns))
    for index, column in enumerate(columns, start=1):
        sheet.column_dimensions[get_column_letter(index)].width = min(max(len(column) + 2, 14), 38)


def export_monthly_plan(plan: MonthlyContentPlan, destination: Path) -> Path:
    """Write Posts and Reels worksheets and return the output path."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    posts = workbook.active
    posts.title = "Posts"
    reels = workbook.create_sheet("Reels")
    _populate(posts, POST_COLUMNS, plan.posts, "D97706")
    _populate(reels, REEL_COLUMNS, plan.reels, "2563EB")
    workbook.properties.title = f"GenForge Content Plan {plan.year}-{plan.month:02d}"
    workbook.properties.subject = "Monthly Instagram posts and Reels plan"
    workbook.save(destination)
    return destination
