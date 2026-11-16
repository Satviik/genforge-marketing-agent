import pytest
from pydantic import ValidationError

from genforge_marketing.profile.models import BusinessProfile, ProductProfile


def test_business_profile_has_genforge_defaults() -> None:
    profile = BusinessProfile()
    assert profile.business_name == "GenForge"
    assert profile.instagram_handle == "@genforge.lab"


def test_product_price_cannot_be_negative() -> None:
    with pytest.raises(ValidationError):
        ProductProfile(name="Test product", price_min_inr=-1)
