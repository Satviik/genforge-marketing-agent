# Campaign Quality Gate

Run:

```bash
genforge-marketing radar campaign-quality-gate --campaign campaigns/bookmark-launch --output output/quality-gate.json
```

Checks brief JSON, product name, core idea, multiple hooks, scene structure and timing, CTA, storyboard, declared artifacts and human review. The gate is advisory; passing makes the draft eligible for human review, never automatically approved or publishable.
