"""Generate first-draft Instagram creative from verified business facts."""

from genforge_marketing.content.models import (
    CarouselSlide,
    InstagramPostContent,
    InstagramReelContent,
    ReelScene,
)
from genforge_marketing.planning.models import MonthlyContentPlan
from genforge_marketing.profile.models import BusinessProfile


def _product(profile: BusinessProfile, name: str):
    for product in profile.products:
        if product.name == name and product.available:
            return product
    raise ValueError(
        f"Product '{name}' is not present and available in the business profile."
    )


def _hashtags(product_name: str, category: str) -> list[str]:
    """Create descriptive tags; these are not claims of current popularity."""
    product_tag = "".join(part.title() for part in product_name.split())
    category_tag = "".join(part.title() for part in category.split())
    return ["#GenForge", "#3DPrinting", "#CustomMade", f"#{product_tag}", f"#{category_tag}"]


def create_post_content(
    profile: BusinessProfile, content_id: str, product_name: str
) -> InstagramPostContent:
    """Create a carousel-ready post draft without inventing product claims."""
    product = _product(profile, product_name)
    description = product.description.strip() or "A custom 3D printed product from GenForge."
    slides = [
        CarouselSlide(
            slide_number=1,
            purpose="Stop the scroll",
            headline=f"Meet {product.name}",
            body_copy="A closer look at this GenForge creation.",
            visual_direction="Hero product photograph on a clean, uncluttered background.",
        ),
        CarouselSlide(
            slide_number=2,
            purpose="Explain the product",
            headline="Designed with details in mind",
            body_copy=description,
            visual_direction="Close-up photographs; show only real product details.",
        ),
        CarouselSlide(
            slide_number=3,
            purpose="Show the making",
            headline="From idea to print",
            body_copy="Show the real design and 3D printing process behind this piece.",
            visual_direction="Use genuine behind-the-scenes workshop footage or photographs.",
        ),
        CarouselSlide(
            slide_number=4,
            purpose="Invite action",
            headline="Have an idea of your own?",
            body_copy=profile.primary_cta,
            visual_direction="Product hero image with a clear, legible call to action.",
        ),
    ]
    return InstagramPostContent(
        content_id=content_id,
        product=product.name,
        concept=f"Product introduction carousel for {product.name}",
        caption=f"Meet {product.name}. {description} {profile.primary_cta}",
        hashtags=_hashtags(product.name, product.category),
        call_to_action=profile.primary_cta,
        carousel_slides=slides,
        visual_prompt=(
            f"Create a premium product-photography layout for {product.name}. "
            "Use the supplied real product image as the exact reference; do not alter "
            "product geometry, invent components, add logos, or render text into the image. "
            "Leave clean negative space for later typography."
        ),
        alt_text=f"{product.name}, a {product.category} product from GenForge.",
        fact_check_notes=[
            "Confirm product description and availability before publishing.",
            "Replace process directions with actual GenForge workshop footage.",
            "Use genuine product photographs; generated imagery must not misrepresent the item.",
        ],
    )


def create_reel_content(
    profile: BusinessProfile, content_id: str, product_name: str
) -> InstagramReelContent:
    """Create a short Reel script and shot list grounded in the product profile."""
    product = _product(profile, product_name)
    description = product.description.strip() or "A custom 3D printed product from GenForge."
    scenes = [
        ReelScene(
            scene_number=1,
            duration_seconds=3,
            shot_description=f"Reveal the finished {product.name} immediately.",
            camera_direction="Quick macro-to-wide reveal; keep the product in focus.",
            on_screen_text=f"An idea, made real: {product.name}",
        ),
        ReelScene(
            scene_number=2,
            duration_seconds=5,
            shot_description="Show close-up details of the actual printed item.",
            camera_direction="Slow controlled pan with soft directional lighting.",
            on_screen_text=description[:70],
        ),
        ReelScene(
            scene_number=3,
            duration_seconds=6,
            shot_description="Show real design, printing, or finishing footage.",
            camera_direction="Use short cuts synchronized to the visual action.",
            voiceover="Every detail starts with an idea.",
        ),
        ReelScene(
            scene_number=4,
            duration_seconds=4,
            shot_description="Finish with a clean product hero shot.",
            camera_direction="Hold a steady frame and allow the call to action to read.",
            on_screen_text=profile.primary_cta,
        ),
    ]
    return InstagramReelContent(
        content_id=content_id,
        product=product.name,
        concept=f"18-second product showcase Reel for {product.name}",
        hook=f"What if your idea became a real 3D printed product?",
        duration_seconds=sum(scene.duration_seconds for scene in scenes),
        scenes=scenes,
        caption=f"{product.name}: {description} {profile.primary_cta}",
        hashtags=_hashtags(product.name, product.category),
        call_to_action=profile.primary_cta,
        audio_direction="Choose licensed upbeat instrumental audio; verify usage rights before posting.",
        cover_visual_prompt=(
            f"Premium editorial cover photograph featuring the supplied real {product.name}. "
            "Preserve its exact appearance. Leave negative space for a title to be added later."
        ),
        fact_check_notes=[
            "Use actual footage of this product and its production process.",
            "Verify all product claims, price and availability before publishing.",
            "Confirm audio rights for the selected track.",
        ],
    )


def create_content_drafts(profile: BusinessProfile, plan: MonthlyContentPlan) -> dict:
    """Create draft creative for every planned post and Reel."""
    posts = [
        create_post_content(profile, item.content_id, item.product)
        for item in plan.posts
    ]
    reels = [
        create_reel_content(profile, item.content_id, item.product)
        for item in plan.reels
    ]
    return {
        "business_name": profile.business_name,
        "year": plan.year,
        "month": plan.month,
        "status": "draft",
        "posts": [item.model_dump(mode="json") for item in posts],
        "reels": [item.model_dump(mode="json") for item in reels],
        "publishing_note": (
            "Draft content only. Human review and approval are required before publishing."
        ),
    }
