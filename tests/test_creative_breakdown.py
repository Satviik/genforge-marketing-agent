from genforge_marketing.intelligence.creative_breakdown import build_creative_breakdown


def test_breakdown_maps_event_roles_and_manual_visual_notes():
    timeline = {"source_file":"sample.mp4","timeline":[
        {"timestamp_seconds":0.5,"event_type":"possible_hook","evidence":"Wait, why?","interpretation":"heuristic"},
        {"timestamp_seconds":2,"event_type":"scene_change","evidence":0.8},
        {"timestamp_seconds":5,"event_type":"explanation_or_process","evidence":"First, we..."},
        {"timestamp_seconds":8,"event_type":"possible_payoff","evidence":"Finished!"}
    ]}
    notes = {"frames":[{"timestamp_seconds":0.5,"observations":{"subject":"printed bookmark"}}]}
    report = build_creative_breakdown(timeline,notes)
    assert report["source_file"] == "sample.mp4"
    assert report["phases"][0]["role"] == "hook_candidate"
    assert report["phases"][0]["visual_observations"]["subject"] == "printed bookmark"
    assert "Hook candidate" in report["observed_structure"]
    assert any("CTA" in x for x in report["observed_structure"])
    assert report["adaptation_guidance"]


def test_breakdown_empty_inputs_is_honest():
    report = build_creative_breakdown()
    assert report["phases"] == []
    assert report["confidence"] == "low"
    assert "retention" in " ".join(report["limitations"])
