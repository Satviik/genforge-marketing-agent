# Campaign dashboard report

Run:

```bash
genforge-marketing radar campaign-dashboard --campaign campaigns/bookmark-launch --output output/campaign-dashboard.json
```

The dashboard is a read-only snapshot combining stage statuses, next action, artifact presence and quality-gate results.

It also exposes an actionable `blockers` list. Each entry identifies the blocker type, relevant stage or artifact/check, the reason, and a suggested action. The `readiness` field is one of:

- `blocked`: one or more artifacts are missing or quality checks have failed.
- `ready_for_human_review`: quality gate checks pass; a human must still approve.
- `needs_review`: no blockers are reported, but the gate does not confirm review readiness.

The report never marks stages complete, approves content, or publishes. Human approval remains required and automated publishing is disabled.
