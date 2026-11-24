from pathlib import Path
import sys
from types import SimpleNamespace

from genforge_marketing.intelligence.transcriber import TranscriptionError, transcribe_audio


def test_transcriber_returns_timestamped_segments(tmp_path, monkeypatch):
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"fake")
    fake_segment = SimpleNamespace(start=0.2, end=1.4, text=" Hello GenForge ")
    fake_info = SimpleNamespace(language="en", language_probability=0.98)
    class FakeModel:
        def __init__(self, *args, **kwargs): pass
        def transcribe(self, *args, **kwargs): return iter([fake_segment]), fake_info
    monkeypatch.setitem(sys.modules, "faster_whisper", SimpleNamespace(WhisperModel=FakeModel))
    report = transcribe_audio(audio)
    assert report["transcript"] == "Hello GenForge"
    assert report["segments"][0]["start_seconds"] == 0.2
    assert report["language"] == "en"


def test_transcriber_missing_file(tmp_path):
    try:
        transcribe_audio(tmp_path / "missing.wav")
    except FileNotFoundError:
        pass
    else:
        assert False, "missing audio should raise FileNotFoundError"


def test_transcriber_missing_optional_dependency(tmp_path, monkeypatch):
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"fake")
    monkeypatch.setitem(sys.modules, "faster_whisper", None)
    try:
        transcribe_audio(audio)
    except TranscriptionError as exc:
        assert "optional" in str(exc).lower()
    else:
        assert False, "missing optional dependency should be explained"
