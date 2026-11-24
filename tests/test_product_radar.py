from genforge_marketing.intelligence.product_radar import ProductCandidate, estimate_material_cost, estimate_gross_margin, score_product, rank_products


def test_cost_and_margin_estimates():
    product = ProductCandidate(name="Custom bookmark", estimated_material_grams=20,
                              material_cost_per_gram=2.0, selling_price=100)
    assert estimate_material_cost(product) == 40
    assert estimate_gross_margin(product) == 0.6


def test_score_handles_missing_margin_data():
    product = ProductCandidate(name="Concept", demand_score=0.9, printability=0.8)
    result = score_product(product)
    assert 0 <= result["score"] <= 1
    assert result["gross_margin_estimate"] is None
    assert result["confidence"] < 1


def test_rank_products_orders_and_discloses_limitations():
    strong = ProductCandidate(name="Personalized desk accessory", demand_score=0.9, printability=0.9,
                             personalization_score=0.95, competition="low",
                             estimated_material_grams=30, material_cost_per_gram=1.5, selling_price=250)
    weak = ProductCandidate(name="Generic ornament", demand_score=0.3, printability=0.5,
                           personalization_score=0.2, competition="high")
    result = rank_products([weak, strong])
    assert result["ranked_products"][0]["candidate"]["name"] == strong.name
    assert result["ranked_products"][0]["score"] > result["ranked_products"][1]["score"]
    assert result["ranked_products"][0]["limitations"]
