"""Product opportunity screening for GenForge; deterministic and explainable."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class ProductCandidate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    trend: str = ""
    concept: str = ""
    printability: float = Field(default=0.5, ge=0, le=1, description="Assessment: easy=1, hard=0")
    estimated_material_grams: float | None = Field(default=None, ge=0)
    estimated_print_hours: float | None = Field(default=None, ge=0)
    material_cost_per_gram: float | None = Field(default=None, ge=0)
    selling_price: float | None = Field(default=None, ge=0)
    personalization_score: float = Field(default=0.5, ge=0, le=1)
    demand_score: float = Field(default=0.5, ge=0, le=1, description="Evidence-based demand estimate, 0-1")
    competition: str = Field(default="unknown", pattern="^(low|medium|high|unknown)$")
    evidence_notes: str = ""


def estimate_material_cost(candidate: ProductCandidate) -> float | None:
    if candidate.estimated_material_grams is None or candidate.material_cost_per_gram is None:
        return None
    return round(candidate.estimated_material_grams * candidate.material_cost_per_gram, 2)


def estimate_gross_margin(candidate: ProductCandidate) -> float | None:
    cost = estimate_material_cost(candidate)
    if cost is None or candidate.selling_price is None or candidate.selling_price <= 0:
        return None
    return round((candidate.selling_price - cost) / candidate.selling_price, 4)


def score_product(candidate: ProductCandidate) -> dict[str, Any]:
    """Score opportunity with available evidence; missing dimensions are excluded and weights renormalized."""
    weights = {
        "demand": 0.30,
        "printability": 0.25,
        "margin": 0.20,
        "personalization": 0.15,
        "competition": 0.10,
    }
    values: dict[str, float] = {"demand": candidate.demand_score, "printability": candidate.printability,
                                 "personalization": candidate.personalization_score}
    margin = estimate_gross_margin(candidate)
    if margin is not None:
        values["margin"] = max(0.0, min(1.0, margin / 0.70))
    if candidate.competition != "unknown":
        values["competition"] = {"low": 1.0, "medium": 0.5, "high": 0.0}[candidate.competition]
    total_weight = sum(weights[key] for key in values)
    score = sum(values[key] * weights[key] for key in values) / total_weight if total_weight else 0.0
    cost = estimate_material_cost(candidate)
    profit_after_material = None if cost is None or candidate.selling_price is None else round(candidate.selling_price - cost, 2)
    return {
        "score": round(score, 4),
        "components": {key: round(value, 4) for key, value in values.items()},
        "confidence": round(total_weight, 4),
        "material_cost_estimate": cost,
        "gross_profit_after_material": profit_after_material,
        "gross_margin_estimate": estimate_gross_margin(candidate),
        "limitations": ["Material cost excludes electricity, machine wear, failed prints, packaging, labor, delivery, taxes, and platform fees.",
                       "Demand and competition scores are inputs, not independently verified market research."],
    }


def rank_products(candidates: list[ProductCandidate]) -> dict[str, Any]:
    ranked = [{"candidate": candidate.model_dump(mode="json"), **score_product(candidate)} for candidate in candidates]
    ranked.sort(key=lambda row: row["score"], reverse=True)
    return {"count": len(ranked), "ranked_products": ranked,
            "note": "Heuristic screening only. Validate demand, prices, costs, and competition before production."}
