# Production handoff

Create a production handoff package after explicit approval:

```bash
genforge-marketing radar campaign-production-handoff --campaign campaigns/bookmark-launch
```

The command requires a recorded approval decision and a brief plus storyboard. It copies these into `production/handoff`, creates a production checklist and manifest, and is idempotent for the checklist. It does not start production or publish.
