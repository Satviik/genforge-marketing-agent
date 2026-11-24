# Frame Visual Notes

Create an editable observation template with one record for every sampled frame in a media-inspection JSON report:

```bash
genforge-marketing radar visual-notes --media output/media-inspection.json --output output/frame-visual-notes.json
```

Fill the observations for each frame from the extracted image. The fields capture shot type, subject, framing, camera angle and movement, subject action, environment, lighting, dominant colors, overlay text, composition, cut/transition, and an analyst's creative-purpose hypothesis.

Keep directly observed facts separate from creative-purpose guesses. Confidence starts at low. This command only creates a template; it does not run visual AI or claim it inspected the frames.
