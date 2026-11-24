from pathlib import Path
from unittest.mock import patch

import json
import subprocess

import pytest

from genforge_marketing.intelligence.media_inspector import MediaInspectionError, inspect_media


def test_inspect_media_metadata_and_frame_index(tmp_path):
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"video")
    frames = tmp_path / "frames"
    frames.mkdir()
    for name in ("frame_0001.jpg", "frame_0002.jpg"):
        (frames / name).write_bytes(b"jpg")
    probe = subprocess.CompletedProcess([], 0, json.dumps({
        "streams": [{"width": 1080, "height": 1920, "r_frame_rate": "30/1", "codec_name": "h264"}],
        "format": {"duration": "12.5"},
    }), "")
    with patch("genforge_marketing.intelligence.media_inspector.shutil.which", side_effect=["ffprobe", "ffmpeg"]), \
         patch("genforge_marketing.intelligence.media_inspector.subprocess.run", side_effect=[probe, subprocess.CompletedProcess([], 0, "", "")]):
        report = inspect_media(video, frames, interval_seconds=2.5)
    assert report["metadata"]["duration_seconds"] == 12.5
    assert report["sampling"]["frame_count"] == 2
    assert report["sampling"]["frames"][1]["approx_timestamp_seconds"] == 2.5


def test_inspect_media_rejects_nonpositive_interval(tmp_path):
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"video")
    with pytest.raises(ValueError):
        inspect_media(video, tmp_path / "frames", 0)


def test_inspect_media_requires_ffmpeg_tools(tmp_path):
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"video")
    with patch("genforge_marketing.intelligence.media_inspector.shutil.which", return_value=None):
        with pytest.raises(MediaInspectionError, match="requires FFmpeg"):
            inspect_media(video, tmp_path / "frames")
