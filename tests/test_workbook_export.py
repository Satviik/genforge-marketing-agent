from datetime import date, time

from openpyxl import load_workbook

from genforge_marketing.planning.models import MonthlyContentPlan, PostPlanItem, ReelPlanItem
from genforge_marketing.workbook.exporter import export_monthly_plan


def test_export_has_posts_and_reels_sheets(tmp_path) -> None:
    plan = MonthlyContentPlan(
        year=2026,
        month=12,
        posts=[PostPlanItem(
            content_id="POST-001",
            planned_date=date(2026, 12, 2),
            planned_time=time(19, 0),
            product="Custom bookmark",
        )],
        reels=[ReelPlanItem(
            content_id="REEL-001",
            planned_date=date(2026, 12, 4),
            planned_time=time(18, 30),
            product="Custom figurine",
            hook="A tiny idea, made real.",
        )],
    )
    path = export_monthly_plan(plan, tmp_path / "content-plan.xlsx")
    workbook = load_workbook(path)

    assert workbook.sheetnames == ["Posts", "Reels"]
    assert workbook["Posts"].max_row == 2
    assert workbook["Reels"].max_row == 2
    assert "creative_brief" in [cell.value for cell in workbook["Posts"][1]]
    assert "hook" in [cell.value for cell in workbook["Reels"][1]]
