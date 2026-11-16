"""Generate a balanced monthly calendar from explicit business inputs."""

import calendar
from datetime import date, time

from genforge_marketing.planning.models import MonthlyContentPlan, PostPlanItem, ReelPlanItem
from genforge_marketing.planning.occasions import OccasionCalendar
from genforge_marketing.profile.models import BusinessProfile


def _scheduled_days(year: int, month: int, count: int) -> list[date]:
    if count < 0:
        raise ValueError("Content count cannot be negative")
    if count == 0:
        return []
    days_in_month = calendar.monthrange(year, month)[1]
    if count > days_in_month:
        raise ValueError("Cannot schedule more than one item per day in a single content type")
    return [
        date(year, month, min(days_in_month, round((index + 0.5) * days_in_month / count)))
        for index in range(count)
    ]


def generate_monthly_plan(
    profile: BusinessProfile,
    year: int,
    month: int,
    post_count: int = 8,
    reel_count: int = 8,
    post_time: time = time(19, 0),
    reel_time: time = time(18, 30),
    occasion_calendar: OccasionCalendar | None = None,
) -> MonthlyContentPlan:
    """Create draft calendar rows; occasion inputs are explicit and never guessed."""
    if not profile.products:
        raise ValueError("Add at least one product to the business profile before planning.")
    products = [product for product in profile.products if product.available]
    if not products:
        raise ValueError("The business profile has no products marked available.")

    if occasion_calendar and (occasion_calendar.year, occasion_calendar.month) != (year, month):
        raise ValueError("Occasion calendar month/year must match the requested plan.")

    post_days = _scheduled_days(year, month, post_count)
    reel_days = _scheduled_days(year, month, reel_count)
    audience = ", ".join(profile.target_audiences)
    plan = MonthlyContentPlan(
        year=year,
        month=month,
        occasions=occasion_calendar.occasions if occasion_calendar else [],
    )

    for index, planned_date in enumerate(post_days, start=1):
        product = products[(index - 1) % len(products)]
        plan.posts.append(
            PostPlanItem(
                content_id=f"POST-{year}{month:02d}-{index:03d}",
                planned_date=planned_date,
                planned_time=post_time,
                post_type="carousel",
                product=product.name,
                objective="awareness",
                audience=audience,
                creative_brief=(
                    f"Create a carousel introducing {product.name}. Use verified product "
                    "photos and only confirmed product details from the business profile."
                ),
                cta=profile.primary_cta,
                notes="Calendar draft. Add final creative and caption, then request approval.",
            )
        )

    for index, planned_date in enumerate(reel_days, start=1):
        product = products[(index - 1) % len(products)]
        plan.reels.append(
            ReelPlanItem(
                content_id=f"REEL-{year}{month:02d}-{index:03d}",
                planned_date=planned_date,
                planned_time=reel_time,
                product=product.name,
                objective="reach",
                audience=audience,
                reel_format="product_showcase",
                hook=f"See how {product.name} comes to life.",
                scene_plan=(
                    "1. Show the finished product. 2. Show close-up details. "
                    "3. Show it in use or demonstrate customization. 4. End with the CTA."
                ),
                cta=profile.primary_cta,
                notes="Calendar draft. Confirm footage, audio rights and caption before approval.",
            )
        )

    return plan
