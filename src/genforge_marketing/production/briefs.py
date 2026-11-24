"""Translate approved content drafts into provider-neutral creative briefs."""
from genforge_marketing.content.models import InstagramPostContent, InstagramReelContent
from genforge_marketing.production.models import AssetKind, CreativeBrief


def image_brief(post: InstagramPostContent, reference_images: list[str] | None = None) -> CreativeBrief:
    """Prepare an image brief; real product photos remain mandatory references."""
    refs = reference_images or []
    return CreativeBrief(
        content_id=post.content_id,
        kind=AssetKind.IMAGE,
        prompt=post.visual_prompt,
        aspect_ratio="4:5",
        reference_images=refs,
        preserve_reference_geometry=True,
        overlay_text=False,
    )


def reel_brief(reel: InstagramReelContent, reference_images: list[str] | None = None) -> CreativeBrief:
    """Prepare a vertical video brief from the script and actual product references."""
    scene_text = " ".join(
        f"Scene {scene.scene_number}: {scene.shot_description} {scene.camera_direction}"
        for scene in reel.scenes
    )
    return CreativeBrief(
        content_id=reel.content_id,
        kind=AssetKind.VIDEO,
        prompt=f"{reel.hook}. {scene_text}. Preserve the supplied product exactly.",
        aspect_ratio="9:16",
        reference_images=reference_images or [],
        duration_seconds=reel.duration_seconds,
        preserve_reference_geometry=True,
        overlay_text=False,
    )
