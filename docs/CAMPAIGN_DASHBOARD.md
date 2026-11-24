# Campaign dashboard report

Run:

```bash
genforge-marketing radar campaign-dashboard --campaign campaigns/bookmark-launch --output output/campaign-dashboard.json
```

The dashboard is a read-only snapshot combining stage statuses, next action, artifact presence and quality-gate results.

It also exposes an actionable `blockers` list. Each entry identifies the blocker type, relevant stage or artifact/check, the reason, and a suggested action. The `readiness` field is one of:

- `blocked`: one or more artifacts are missing or critical quality checks have failed.
- `ready_for_human_review`: content checks pass; the human review step is still pending or required.
- `needs_review`: no blockers are reported, but the gate does not confirm review readiness.

Human review is surfaced separately in `review_items`, not counted as a content blocker. A campaign can be ready for human review without being approved or publishable.

The report never marks stages complete, approves content, or publishes. Human approval remains required and automated publishing is disabled.
