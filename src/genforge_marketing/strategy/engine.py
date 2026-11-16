"""Generate a grounded baseline strategy from verified business profile inputs.

This deterministic strategy is the fallback and validation baseline for a future
LLM strategist. It intentionally avoids inventing customer testimonials or metrics.
"""

from genforge_marketing.profile.models import BusinessProfile
from genforge_marketing.strategy.models import (
    AudienceMessage,
    ContentPillar,
    MonthlyStrategy,
)


def generate_strategy(profile: BusinessProfile, year: int, month: int) -> MonthlyStrategy:
    """Build a month-specific strategy using only supplied profile facts."""
    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12")

    available_products = [product for product in profile.products if product.available]
    if not available_products:
        raise ValueError("At least one available product is required for strategy generation.")

    product_names = [product.name for product in available_products]
    differentiators = [
        fact for product in available_products for fact in product.differentiators
    ]
    audiences = profile.target_audiences or ["People interested in custom 3D printed products"]
    goals = profile.content_goals or ["awareness", "inquiries"]

    pillars = [
        ContentPillar(
            name="Product spotlight",
            purpose="Make the available product range easy to discover and understand.",
            recommended_share=0.30,
            formats=["carousel", "single_image", "product_showcase_reel"],
            example_angles=[
                f"Feature {name} with verified photos and product details."
                for name in product_names[:4]
            ],
        ),
        ContentPillar(
            name="Customization and making",
            purpose="Explain the customisation process and show how an idea becomes a physical item.",
            recommended_share=0.25,
            formats=["process_reel", "before_after_carousel", "workbench_story"],
            example_angles=[
                "Show a real design-to-print sequence.",
                "Explain which design details customers can request.",
            ],
        ),
        ContentPillar(
            name="Useful inspiration",
            purpose="Help audiences discover practical or giftable uses for 3D printed products.",
            recommended_share=0.20,
            formats=["educational_carousel", "tips_reel"],
            example_angles=[
                "Show a product solving a clearly demonstrated everyday use case.",
                "Share a design detail and explain why it matters.",
            ],
        ),
        ContentPillar(
            name="Behind the scenes",
            purpose="Build familiarity by showing the real design, printing and finishing workflow.",
            recommended_share=0.15,
            formats=["behind_the_scenes_reel", "photo_story"],
            example_angles=[
                "Show printer preparation, a print in progress, or finishing.",
                "Explain one genuine production challenge and how it was handled.",
            ],
        ),
        ContentPillar(
            name="Community and proof",
            purpose="Build trust using genuine customer feedback and completed orders when available.",
            recommended_share=0.10,
            formats=["customer_feature", "order_story"],
            example_angles=[
                "Feature a customer-approved photo or review, only when supplied.",
                "Show a completed order with customer permission.",
            ],
        ),
    ]

    audience_messages = [
        AudienceMessage(
            audience=audience,
            needs=["Understand product usefulness", "See quality and customisation options"],
            message=(
                f"GenForge turns ideas into tangible 3D printed products. "
                f"Explore: {', '.join(product_names[:5])}."
            ),
            proof_points=differentiators,
        )
        for audience in audiences
    ]

    guardrails = [
        "Use only product details, prices and capabilities present in the business profile.",
        "Do not invent customer reviews, testimonials, order volumes or performance metrics.",
        "Obtain customer permission before featuring their name, image or order.",
        "Confirm product availability and price before publishing any sales claim.",
        "Use licensed or platform-cleared audio and visual assets.",
        "Every item remains a draft until a human reviews and approves it.",
    ]
    if profile.facts_to_avoid_claiming:
        guardrails.extend(
            f"Do not claim: {fact}" for fact in profile.facts_to_avoid_claiming
        )
    assumptions = []
    if not profile.business_summary:
        assumptions.append("Business summary is missing; positioning is based on the product catalogue.")
    if not profile.target_audiences:
        assumptions.append("No target audiences supplied; a broad custom 3D-printing audience is used.")
    if not differentiators:
        assumptions.append("No product differentiators supplied; avoid unsupported quality or uniqueness claims.")

    return MonthlyStrategy(
        business_name=profile.business_name,
        year=year,
        month=month,
        primary_goal=goals[0],
        supporting_goals=goals[1:],
        positioning_summary=(
            profile.business_summary.strip()
            or "GenForge creates custom 3D printed products from customer ideas."
        ),
        pillars=pillars,
        audience_messages=audience_messages,
        cadence_recommendation=(
            "Use the requested post and Reel counts as the publishing cadence. "
            "Distribute the five content pillars across the month; review performance "
            "before increasing frequency."
        ),
        creative_direction=profile.brand_voice,
        guardrails=guardrails,
        assumptions=assumptions,
    )
