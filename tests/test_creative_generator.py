from genforge_marketing.intelligence.creative_generator import generate_original_reel


def test_original_reel_brief_has_timed_scenes_and_reference_adaptation():
    breakdown = {"phases": [{"role": "hook_candidate"}, {"role": "visual_reset"}],
                 "adaptation_guidance": ["Reuse mechanics, not wording."]}
    brief = generate_original_reel("Custom bookmark", "Personalized design", duration_seconds=20,
                                  creative_breakdown=breakdown)
    assert brief["status"] == "draft_for_review"
    assert brief["provider"] == "deterministic_local_template"
    scenes = brief["production_plan"]["scenes"]
    assert scenes[0]["start_seconds"] == 0
    assert scenes[-1]["end_seconds"] == 20
    assert all(scene["end_seconds"] > scene["start_seconds"] for scene in scenes)
    assert brief["reference_adaptation"]["source_structure_roles"] == ["hook_candidate", "visual_reset"]


def test_generator_validates_product_and_duration():
    import pytest
    with pytest.raises(ValueError):
        generate_original_reel(" ")
    with pytest.raises(ValueError):
        generate_original_reel("Widget", duration_seconds=5)
