# Campaign Orchestrator (workflow status MVP)

The orchestrator tracks progress in the campaign manifest and reports the next incomplete stage. It does not execute production or publish automatically.

Stages: research, analysis, brief, storyboard, production, review, published, metrics, learning.

## CLI

```bash
genforge-marketing radar campaign-status --campaign campaigns/bookmark-launch
genforge-marketing radar campaign-stage --campaign campaigns/bookmark-launch/campaign.json --stage research --status completed --note "Research reviewed"
```

Human approval is required for review and publishing. Publishing is not automated.
