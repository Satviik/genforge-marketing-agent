# Campaign stage task scaffold

Use `campaign-start-stage` to create a starter file for the planner's next stage, or specify a stage.

```bash
genforge-marketing radar campaign-start-stage --campaign campaigns/bookmark-launch
genforge-marketing radar campaign-start-stage --campaign campaigns/bookmark-launch --stage brief
```

Creation is non-destructive: existing files are never overwritten. The command creates one template file only and does not mark the stage complete or in progress.
