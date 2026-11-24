from genforge_marketing.intelligence.visual_notes import build_visual_notes_template, validate_visual_notes


def test_visual_notes_template_preserves_frame_refs_and_empty_fields():
    media = {"source_file":"reel.mp4","sampling":{"frames":[
        {"approx_timestamp_seconds":1.5,"file":"frame-001.jpg"},
        {"approx_timestamp_seconds":3.0,"file":"frame-002.jpg"}]}}
    template = build_visual_notes_template(media)
    assert len(template["frames"]) == 2
    assert template["frames"][0]["timestamp_seconds"] == 1.5
    assert template["frames"][0]["image_file"] == "frame-001.jpg"
    assert template["frames"][0]["observations"]["camera_angle"] == ""
    assert template["frames"][0]["observations"]["dominant_colors"] == []
    assert validate_visual_notes(template) == []


def test_visual_notes_validation_detects_bad_timestamps_and_duplicate_indices():
    notes = {"frames":[
        {"frame_index":0,"timestamp_seconds":-1,"observations":{}},
        {"frame_index":0,"timestamp_seconds":"not-a-number","observations":{}}
    ]}
    errors = validate_visual_notes(notes)
    assert any("cannot be negative" in error for error in errors)
    assert any("must be numeric" in error for error in errors)
    assert any("duplicate frame_index" in error for error in errors)
