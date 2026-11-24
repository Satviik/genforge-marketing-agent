from genforge_marketing.intelligence.storyboard import build_storyboard


def test_storyboard_renders_events_and_escapes_html():
    report = {"source_file":"demo <reel>.mp4","duration_seconds":8,
        "evidence_summary":{"sampled_frames":1,"scene_changes":1},
        "timeline":[
          {"timestamp_seconds":0.5,"event_type":"sampled_frame","evidence":"frame-001.jpg","interpretation":"frame sample"},
          {"timestamp_seconds":2,"event_type":"possible_hook","evidence":"Wait <what>?","interpretation":"heuristic"}
        ]}
    html = build_storyboard(report, "frames")
    assert "Reel Storyboard" in html
    assert "00:00.50" in html
    assert "frames/frame-001.jpg" in html
    assert "Wait &lt;what&gt;?" in html
    assert "demo &lt;reel&gt;.mp4" in html
    assert "viewer-retention measurement" in html


def test_storyboard_handles_empty_report():
    html = build_storyboard({})
    assert "No events were present" in html
