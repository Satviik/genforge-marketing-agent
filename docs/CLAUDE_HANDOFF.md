# Claude Handoff Export

Export an original Reel creative brief and optional evidence reports into a self-contained Markdown handoff package for Claude. The exporter does not call Claude, any model, or paid API. It writes a reviewable prompt package containing product/campaign facts, concepts/hooks, scene plan, shot list, caption/CTA, originality guardrails, and optional creative breakdown/timeline/manual frame observations.

## Command

```bash
genforge-marketing radar export-claude --brief output/original-reel-brief.json --breakdown output/creative-breakdown.json --timeline output/reel-timeline.json --visual-notes output/frame-visual-notes.json --output output/claude-creative-handoff.md
```

Optional research inputs may be omitted. Open the Markdown and paste or attach it to Claude. Human review is required before filming or publishing.
