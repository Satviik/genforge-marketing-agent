from genforge_marketing.intelligence.reel_autopsy import BeatObservation, ReferenceInput, build_autopsy


def sample_reference():
    return ReferenceInput(
        title="DIY desk transformation",
        platform="Instagram",
        format="reel",
        objective="product discovery",
        hook_observation="Shows the cluttered desk and finished result immediately.",
        hook_text="Wait until you see this desk upgrade",
        beats=[
            BeatObservation(timestamp_start_seconds=0, timestamp_end_seconds=2, visual_description="Before and after split", inferred_role="hook", retention_mechanism="visual contrast"),
            BeatObservation(timestamp_start_seconds=2, timestamp_end_seconds=5, spoken_text="I needed a place for everything", inferred_role="problem"),
            BeatObservation(timestamp_start_seconds=5, timestamp_end_seconds=10, action="Print and assemble organizer", inferred_role="process"),
            BeatObservation(timestamp_start_seconds=10, timestamp_end_seconds=13, visual_description="Finished organizer on desk", inferred_role="payoff"),
        ],
        payoff_observation="Clean desk reveal",
        cta_observation="Ask viewers to comment with their desk setup",
        caption="A satisfying desk upgrade. What would you change?",
    )


def test_autopsy_reconstructs_timeline_and_roles():
    report = build_autopsy(sample_reference())
    assert report["report_type"] == "reel_autopsy"
    assert report["descriptive_analysis"]["beat_count"] == 4
    assert report["observations"]["role_sequence"] == ["hook", "problem", "process", "payoff"]
    assert report["timeline"][0]["start_seconds"] == 0
    assert report["timeline"][-1]["role"] == "payoff"


def test_autopsy_contains_original_adaptation_worksheet_and_limitations():
    report = build_autopsy(sample_reference())
    worksheet = report["adaptation_worksheet"]
    assert worksheet["mechanism_to_adapt"] == ""
    assert "original GenForge footage" in worksheet["quality_checks"][3]
    assert any("does not fetch or inspect" in item for item in report["limitations"])


def test_autopsy_handles_missing_beats():
    report = build_autopsy(ReferenceInput(title="Text-only post", format="carousel"))
    assert report["timeline"] == []
    assert report["descriptive_analysis"]["beat_timing_available"] is False
    assert report["observations"]["role_counts"] == {}
