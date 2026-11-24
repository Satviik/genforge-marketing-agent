# Campaign production tasks

Tasks are stored in the approved campaign's production handoff manifest. No external service or publishing action is used.

```bash
genforge-marketing radar campaign-task-add --campaign campaigns/bookmark-launch --title "Film product close-up" --assignee "Satvik" --priority high --due-date 2026-12-01
genforge-marketing radar campaign-task-list --campaign campaigns/bookmark-launch
genforge-marketing radar campaign-task-update --campaign campaigns/bookmark-launch --task-id task-001 --status in_progress --notes "Filming started"
```

Task states: `todo`, `in_progress`, `completed`, `blocked`. Tasks require a recorded approval and production handoff.
