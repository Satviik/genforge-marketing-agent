# Campaign creative pipeline

Build a campaign's original creative brief and Markdown storyboard in one local command:

```bash
genforge-marketing radar campaign-build-creative --campaign campaigns/bookmark-launch --duration 20
```

Artifacts:
- `drafts/creative-brief.json`
- `production/storyboard.md`

The command registers both in campaign.json and sets the brief stage to `in_progress`, not completed. Existing outputs are never overwritten. It uses deterministic templates, no AI provider or API call, and requires human review.
