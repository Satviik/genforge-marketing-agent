# Reel Timeline Reconstruction

Merge existing local media-analysis JSON reports into one chronological evidence timeline.

## Example

Run any available stages first:

```bash
genforge-marketing radar inspect-media --input reel.mp4 --output output/media.json --frames-dir output/frames
genforge-marketing radar detect-scenes --input reel.mp4 --output output/scenes.json
genforge-marketing radar inspect-audio --input reel.mp4 --audio-output output/audio.wav --output output/audio.json
genforge-marketing radar transcribe-audio --input output/audio.wav --output output/transcript.json --model base
```

Then combine them:

```bash
genforge-marketing radar reconstruct-timeline --media output/media.json --scenes output/scenes.json --audio output/audio.json --transcript output/transcript.json --output output/timeline.json
```

Each source is optional, but at least one report must be supplied. Events are sorted by timestamp and include sampled frames, scene-change candidates, silence intervals and transcript segments. A few text heuristics label transcript segments as possible hook, explanation/process or possible payoff; these are not semantic AI judgments and require human review.

This module does not yet analyze image content, music, emotion, retention, or audience response. It is a chronology and evidence merger only.
