# Campaign execution planner

`campaign-plan` combines campaign progress with the artifact audit and proposes a next step. It is deterministic and local-only.

```bash
genforge-marketing radar campaign-plan --campaign campaigns/bookmark-launch
```

The plan shows the next incomplete stage, guidance, any missing artifacts declared for that stage, and whether human approval is required. It never changes manifest state, creates files, invokes external services or publishes.
