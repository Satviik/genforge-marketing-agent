# Reel Autopsy (MVP)

Reel Autopsy converts **supplied observations and text** into a structured content blueprint. It is not an automatic video downloader, frame extractor, or transcription system yet.

## Input

Create a JSON file with reference metadata, observations, and timestamped beats. Example:

```json
{
  "title": "DIY desk transformation",
  "platform": "Instagram",
  "url": "https://www.instagram.com/reel/example/",
  "format": "reel",
  "objective": "product discovery",
  "metrics": {"views": 100000, "likes": 8000, "comments": 320},
  "hook_observation": "Shows clutter and finished result in the first moments",
  "hook_text": "Wait until you see this desk upgrade",
  "beats": [
    {"timestamp_start_seconds": 0, "timestamp_end_seconds": 2, "visual_description": "Before/after split", "inferred_role": "hook", "retention_mechanism": "visual contrast"},
    {"timestamp_start_seconds": 2, "timestamp_end_seconds": 5, "spoken_text": "I needed a place for everything", "inferred_role": "problem"},
    {"timestamp_start_seconds": 5, "timestamp_end_seconds": 10, "action": "Print and assemble organizer", "inferred_role": "process"},
    {"timestamp_start_seconds": 10, "timestamp_end_seconds": 13, "visual_description": "Finished organizer", "inferred_role": "payoff"}
  ],
  "payoff_observation": "Clean desk reveal",
  "cta_observation": "Ask viewers to comment with their setup",
  "caption": "A satisfying desk upgrade. What would you change?",
  "visual_style_notes": ["macro product details", "warm desk lighting"],
  "editing_notes": ["cut on action", "fast opening"],
  "audio_notes": ["light instrumental"]
}
```

## Run

```bash
genforge-marketing radar autopsy --input data/reel-reference.json --output output/reel-autopsy.json
```

The output includes source metadata, observation summary, timestamped timeline, descriptive text counts, role sequence, limitations, and an **adaptation worksheet** with fields for a GenForge angle, product, original script beats, shot list, editing plan, caption, CTA, and quality checks.

## Evidence and boundaries

- The tool does not infer missing footage or timestamps.
- The beat labels and descriptions are analyst-provided.
- Text counts are descriptive—not retention or virality predictions.
- Source metrics are not independently verified.
- The worksheet is intentionally blank for original GenForge creative decisions.
