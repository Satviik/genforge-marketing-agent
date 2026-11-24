# Local Media Inspection

The local media pipeline uses FFprobe to read video metadata, FFmpeg to sample frames, and FFmpeg's scene filter to detect visual changes. It does not use an external API.

## Requirements

- FFmpeg and FFprobe installed and available on `PATH`
- A local video file readable by FFmpeg

## Usage

```bash
genforge-marketing radar inspect-media --input path/to/reel.mp4 --output output/media-inspection.json --frames-dir output/media-frames --interval 2
```

- `--input`: local video source
- `--output`: metadata and frame-index JSON report
- `--frames-dir`: sampled JPEG output directory
- `--interval`: sampling interval in seconds (default: 2)

The JSON includes duration, width/height, video frame rate, codec, approximate timestamps, and relative frame paths. Frame sampling is mechanical; timestamps are approximate and may not land on scene boundaries.

## Scene-change detection

Detect candidate cuts or visual changes:

```bash
genforge-marketing radar detect-scenes --input path/to/reel.mp4 --threshold 0.30 --output output/scene-changes.json
```

Threshold ranges from 0 to 1; tune it for the footage. The report records timestamps and available scene scores. This is visual-change detection, not semantic scene understanding; motion, flashes, or camera changes can create false positives.

## Audio extraction and silence detection

Extract a local mono 16 kHz WAV and detect silence intervals:

```bash
genforge-marketing radar inspect-audio --input path/to/reel.mp4 --audio-output output/reel-audio.wav --output output/audio-inspection.json --noise-db -35 --min-silence 0.35
```

- `--noise-db`: silence threshold (default `-35` dB)
- `--min-silence`: minimum silence duration (default `0.35` seconds)

The output contains the extracted WAV path and approximate silence intervals. This can help spot pauses and pacing, but it does not transcribe speech, classify music, or infer creative intent. FFmpeg must be installed and available on `PATH`.

## Local speech transcription

Install the optional transcription dependency (no paid API):

```bash
pip install -e ".[transcription]"
```

Transcribe the extracted WAV using a local Whisper model:

```bash
genforge-marketing radar transcribe-audio --input output/reel-audio.wav --output output/transcription.json --model base --device cpu --language en
```

Model weights are downloaded on first use and consume disk space. Model size controls accuracy/speed; `tiny` and `base` are lighter, while larger models need more resources. `--device cuda` is optional for compatible local CUDA setups. Output includes timestamped text segments and language detection. No paid API is used.

## Current limitations

- No visual understanding/classification of extracted frames.
- Optional local speech transcription is implemented through faster-whisper; visual frame understanding remains unimplemented.
- Scene changes are visual-change candidates only; semantic labels and narrative roles still require interpretation.
- Does not fetch media from social URLs.
- Use media only when you have rights or permission to analyze it.
- Sampled frames are evidence artifacts for later structural analysis; they are not labeled as hook, proof, payoff, or CTA automatically.
