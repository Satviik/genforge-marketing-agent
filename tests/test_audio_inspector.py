from pathlib import Path
from unittest.mock import patch
import subprocess

import pytest

from genforge_marketing.intelligence.media_inspector import MediaInspectionError
from genforge_marketing.intelligence.audio_inspector import extract_audio_and_detect_silence


def test_audio_inspection_parses_silence_intervals(tmp_path):
    source = tmp_path / "reel.mp4"
    source.write_bytes(b"fake")
    audio = tmp_path / "out" / "audio.wav"
    logs = "silence_start: 1.25\\nsilence_end: 2.5 | silence_duration: 1.25\\nsilence_start: 4.0"
    success = subprocess.CompletedProcess([], 0, "", "")
    detect = subprocess.CompletedProcess([], 0, "", logs)
    with patch("genforge_marketing.intelligence.audio_inspector.shutil.which", return_value="ffmpeg"), \
         patch("genforge_marketing.intelligence.audio_inspector.subprocess.run", side_effect=[success, detect]):
        report = extract_audio_and_detect_silence(source, audio)
    assert report["silence_detection"]["interval_count"] == 2
    assert report["silence_detection"]["intervals"][0]["duration_seconds"] == 1.25
    assert report["silence_detection"]["intervals"][1]["end_seconds"] is None


def test_audio_inspection_validates_thresholds(tmp_path):
    source = tmp_path / "reel.mp4"
    source.write_bytes(b"fake")
    with pytest.raises(ValueError):
        extract_audio_and_detect_silence(source, tmp_path / "a.wav", noise_db=5)
    with pytest.raises(ValueError):
        extract_audio_and_detect_silence(source, tmp_path / "a.wav", min_silence_seconds=0)


def test_audio_inspection_missing_ffmpeg(tmp_path):
    source = tmp_path / "reel.mp4"
    source.write_bytes(b"fake")
    with patch("genforge_marketing.intelligence.audio_inspector.shutil.which", return_value=None):
        with pytest.raises(MediaInspectionError, match="requires FFmpeg"):
            extract_audio_and_detect_silence(source, tmp_path / "a.wav")
