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

## Current limitations

- No visual understanding/classification of extracted frames.
- No audio extraction or speech transcription.
- Scene changes are visual-change candidates only; semantic labels and narrative roles still require interpretation.
- Does not fetch media from social URLs.
- Use media only when you have rights or permission to analyze it.
- Sampled frames are evidence artifacts for later structural analysis; they are not labeled as hook, proof, payoff, or CTA automatically.
