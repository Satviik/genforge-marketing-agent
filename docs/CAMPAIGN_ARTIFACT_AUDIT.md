# Campaign artifact audit

Declare paths in `campaign.json` under an `artifacts` object. Paths are relative to the campaign workspace.

```json
{
  "artifacts": {
    "brief": ["creative-brief.md"],
    "storyboard": ["storyboard.html"],
    "production": ["assets/final.mp4"]
  }
}
```

Run:

```bash
genforge-marketing radar campaign-audit --campaign campaigns/bookmark-launch
```

The audit checks existence of declared paths only; it does not validate content quality or automatically mark stages complete.
