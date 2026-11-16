from genforge_marketing.profile.models import BusinessProfile, ProductProfile
from genforge_marketing.strategy.engine import generate_strategy


def test_strategy_has_five_balanced_content_pillars() -> None:
    profile = BusinessProfile(
        business_summary="Custom 3D printed products designed around customer ideas.",
        target_audiences=["gift buyers", "collectors"],
        content_goals=["inquiries", "awareness", "sales"],
        products=[
            ProductProfile(
                name="Custom bookmark",
                differentiators=["Personalised design", "Made to order"],
            )
        ],
    )
    strategy = generate_strategy(profile, 2026, 12)

    assert strategy.primary_goal == "inquiries"
    assert len(strategy.pillars) == 5
    assert round(sum(p.recommended_share for p in strategy.pillars), 2) == 1.0
    assert len(strategy.audience_messages) == 2
    assert "Personalised design" in strategy.audience_messages[0].proof_points
    assert any("human" in item.lower() for item in strategy.guardrails)


def test_strategy_does_not_invent_social_proof() -> None:
    profile = BusinessProfile(
        products=[ProductProfile(name="Custom keychain")],
        facts_to_avoid_claiming=["waterproof"],
    )
    strategy = generate_strategy(profile, 2026, 12)

    assert any("customer permission" in item.lower() for item in strategy.guardrails)
    assert any("Do not claim: waterproof" == item for item in strategy.guardrails)
    assert strategy.assumptions


def test_strategy_requires_available_product() -> None:
    profile = BusinessProfile(products=[ProductProfile(name="Out of stock", available=False)])
    try:
        generate_strategy(profile, 2026, 12)
    except ValueError as exc:
        assert "available product" in str(exc)
    else:
        raise AssertionError("Strategy should reject profiles without available products")
