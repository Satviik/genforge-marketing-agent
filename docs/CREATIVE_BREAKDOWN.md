# Creative Breakdown

Build a structured creative sequence from a reconstructed timeline and optional manually completed visual notes:

```bash
genforge-marketing radar creative-breakdown --timeline output/reel-timeline.json --visual-notes output/frame-visual-notes.json --output output/creative-breakdown.json
```

The report groups events into hook candidates, visual resets, process/explanation, pauses, payoff candidates and supporting events. It may attach manual visual observations to timeline events when timestamps are close.

The tool uses event labels and transcript text heuristics; it does not infer CTA, retention, audience psychology or causal virality. Use its adaptation guidance to develop an original GenForge creative, not copy the source.
