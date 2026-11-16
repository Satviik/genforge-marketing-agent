"""Deterministic baseline scoring for content opportunities."""

from genforge_marketing.models.opportunity import TrendOpportunity


def score_opportunity(item: TrendOpportunity) -> float:
    """Score an opportunity from 0 to 1 using available engagement evidence.

    This transparent baseline is not an ML prediction; later iterations can
    calibrate weights against actual GenForge content performance.
    """
    engagement = 0.0
    if item.views and item.views > 0:
        interactions = (item.likes or 0) + (item.comments or 0)
        engagement = min(interactions / item.views * 20, 1.0)

    return round(0.65 * item.relevance_score + 0.35 * engagement, 4)
