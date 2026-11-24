from genforge_marketing.planning.generator import generate_monthly_plan
from genforge_marketing.profile.models import BusinessProfile, ProductProfile


def test_monthly_plan_generates_separate_post_and_reel_calendars() -> None:
    profile = BusinessProfile(
        target_audiences=["students", "collectors"],
        products=[
            ProductProfile(name="Custom bookmark"),
            ProductProfile(name="Custom figurine"),
        ],
    )
    plan = generate_monthly_plan(profile, 2026, 12, post_count=6, reel_count=8)

    assert len(plan.posts) == 6
    assert len(plan.reels) == 8
    assert {item.approval_status.value for item in plan.posts} == {"draft"}
    assert {item.approval_status.value for item in plan.reels} == {"draft"}
    assert {item.product for item in plan.posts} == {"Custom bookmark", "Custom figurine"}
    assert all(item.planned_date.month == 12 for item in plan.posts + plan.reels)


def test_planner_requires_available_products() -> None:
    profile = BusinessProfile(products=[])
    try:
        generate_monthly_plan(profile, 2026, 12)
    except ValueError as exc:
        assert "at least one product" in str(exc)
    else:
        raise AssertionError("Planner should reject an empty product catalogue")
