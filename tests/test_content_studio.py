from datetime import date, time

import pytest

from genforge_marketing.content.studio import (
    create_content_drafts,
    create_post_content,
    create_reel_content,
)
from genforge_marketing.planning.models import MonthlyContentPlan, PostPlanItem, ReelPlanItem
from genforge_marketing.profile.models import BusinessProfile, ProductProfile


@pytest.fixture
def profile() -> BusinessProfile:
    return BusinessProfile(
        business_summary="Custom 3D printed products made from ideas.",
        primary_cta="DM GenForge for a custom order",
        products=[
            ProductProfile(
                name="Custom bookmark",
                description="A personalised 3D printed bookmark.",
                category="bookmark",
            )
        ],
    )


def test_post_content_has_four_carousel_slides_and_fact_checks(profile) -> None:
    post = create_post_content(profile, "POST-001", "Custom bookmark")
    assert len(post.carousel_slides) == 4
    assert post.carousel_slides[0].headline == "Meet Custom bookmark"
    assert "DM GenForge" in post.call_to_action
    assert post.fact_check_notes


def test_reel_content_has_timed_scenes(profile) -> None:
    reel = create_reel_content(profile, "REEL-001", "Custom bookmark")
    assert reel.duration_seconds == sum(scene.duration_seconds for scene in reel.scenes)
    assert 5 <= reel.duration_seconds <= 90
    assert reel.hook
    assert reel.audio_direction


def test_content_studio_rejects_unknown_or_unavailable_products(profile) -> None:
    with pytest.raises(ValueError, match="not present and available"):
        create_post_content(profile, "POST-002", "Imaginary product")


def test_create_content_drafts_covers_both_sheets(profile) -> None:
    plan = MonthlyContentPlan(
        year=2026,
        month=12,
        posts=[PostPlanItem(
            content_id="POST-001",
            planned_date=date(2026, 12, 2),
            planned_time=time(19),
            product="Custom bookmark",
        )],
        reels=[ReelPlanItem(
            content_id="REEL-001",
            planned_date=date(2026, 12, 3),
            planned_time=time(18, 30),
            product="Custom bookmark",
        )],
    )
    drafts = create_content_drafts(profile, plan)
    assert drafts["status"] == "draft"
    assert len(drafts["posts"]) == 1
    assert len(drafts["reels"]) == 1
    assert "Human review" in drafts["publishing_note"]
