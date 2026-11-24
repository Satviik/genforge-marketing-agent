# Reel Storyboard

Render a reconstructed timeline into a portable HTML review page.

```bash
genforge-marketing radar storyboard --timeline output/reel-timeline.json --frames-dir output/frames --output output/reel-storyboard.html
```

The report includes event timestamps, event labels, evidence text, a compact count summary, and sampled-frame thumbnails when image paths are available. It is a local static HTML file and does not require a server or send data elsewhere.

**Frame path note:** the frame directory is prepended to relative frame filenames in the report. If your media report stores nested relative paths, keep the same folder layout under that directory.

Event labels remain heuristic. The storyboard is a review aid, not automated visual understanding, and it cannot measure retention or audience reaction.
