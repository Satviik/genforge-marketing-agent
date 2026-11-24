from pathlib import Path
from unittest.mock import patch
import subprocess

import pytest

from genforge_marketing.intelligence.media_inspector import MediaInspectionError
from genforge_marketing.intelligence.scene_detector import detect_scene_changes


def test_detect_scene_changes_parses_timestamp_and_score(tmp_path):
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"video")
    stderr = "[Parsed_showinfo_1] pts_time:2.500 lavfi.scene_score:0.61\\n[Parsed_showinfo_1] pts_time:7.000 lavfi.scene_score:0.83"
    result = subprocess.CompletedProcess([], 0, "", stderr)
    with patch("genforge_marketing.intelligence.scene_detector.shutil.which", return_value="ffmpeg"), \
         patch("genforge_marketing.intelligence.scene_detector.subprocess.run", return_value=result):
        report = detect_scene_changes(video, 0.3)
    assert report["scene_change_count"] == 2
    assert report["scene_changes"][0]["timestamp_seconds"] == 2.5
    assert report["scene_changes"][1]["scene_score"] == 0.83


def test_scene_detector_threshold_validation(tmp_path):
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"video")
    with pytest.raises(ValueError):
        detect_scene_changes(video, 1.5)


def test_scene_detector_missing_ffmpeg(tmp_path):
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"video")
    with patch("genforge_marketing.intelligence.scene_detector.shutil.which", return_value=None):
        with pytest.raises(MediaInspectionError, match="requires FFmpeg"):
            detect_scene_changes(video)
