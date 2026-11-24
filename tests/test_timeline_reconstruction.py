from genforge_marketing.intelligence.timeline_reconstruction import reconstruct_timeline


def test_reconstruction_merges_media_evidence_and_transcript():
    media = {"source_file":"demo.mp4","metadata":{"duration_seconds":12},
              "sampling":{"frames":[{"approx_timestamp_seconds":0,"file":"f0.jpg"},{"approx_timestamp_seconds":4,"file":"f1.jpg"}]}}
    scenes = {"scene_changes":[{"timestamp_seconds":3.5,"scene_score":0.8}]}
    audio = {"silence_detection":{"intervals":[{"start_seconds":5,"end_seconds":5.4,"duration_seconds":0.4}]}}
    transcript = {"segments":[{"start_seconds":0.5,"end_seconds":2,"text":"Wait, why is this tiny?"},{"start_seconds":7,"end_seconds":9,"text":"Finally the result is finished."}]}
    report = reconstruct_timeline(media,scenes,audio,transcript)
    assert report["analysis_type"] == "reel_timeline_reconstruction"
    assert report["source_file"] == "demo.mp4"
    assert report["evidence_summary"]["sampled_frames"] == 2
    assert report["evidence_summary"]["scene_changes"] == 1
    assert report["evidence_summary"]["silence_intervals"] == 1
    assert any(e["event_type"] == "possible_hook" for e in report["timeline"])
    assert any(e["event_type"] == "possible_payoff" for e in report["timeline"])
    assert report["timeline"] == sorted(report["timeline"],key=lambda e:e["timestamp_seconds"])


def test_reconstruction_allows_missing_sources():
    report = reconstruct_timeline()
    assert report["timeline"] == []
    assert report["event_count"] == 0
    assert report["limitations"]
