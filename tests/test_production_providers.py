import pytest

from genforge_marketing.production.models import AssetKind, CreativeBrief
from genforge_marketing.production.providers import CreativeProviderError, DisabledCreativeProvider


def test_disabled_provider_never_returns_fake_asset():
    brief = CreativeBrief(content_id="post-1", prompt="Product photo", kind=AssetKind.IMAGE)
    with pytest.raises(CreativeProviderError, match="not configured"):
        DisabledCreativeProvider().generate(brief)


def test_brief_defaults_to_preserving_product_geometry_and_no_text():
    brief = CreativeBrief(content_id="post-1", prompt="Studio shot", kind=AssetKind.IMAGE)
    assert brief.preserve_reference_geometry is True
    assert brief.overlay_text is False
    assert brief.reference_images == []
