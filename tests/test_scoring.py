from genforge_marketing.intelligence.scoring import score_opportunity
from genforge_marketing.models.opportunity import TrendOpportunity


def test_score_is_bounded_and_rewards_relevance() -> None:
    low = TrendOpportunity(topic="low", source="instagram", relevance_score=0.1)
    high = TrendOpportunity(topic="high", source="instagram", relevance_score=0.9)

    assert 0 <= score_opportunity(low) <= 1
    assert score_opportunity(high) > score_opportunity(low)


def test_engagement_contributes_to_score() -> None:
    item = TrendOpportunity(
        topic="test",
        source="instagram",
        relevance_score=0.5,
        views=1000,
        likes=100,
        comments=20,
    )

    assert score_opportunity(item) > 0.325
