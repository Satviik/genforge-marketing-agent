# Production tracking

After an approved campaign has a production handoff, record manual production status using the Python API:

```python
from genforge_marketing.intelligence.campaign_production_tracking import update_production_status
update_production_status("campaigns/bookmark-launch", "in_progress", "Filming started")
update_production_status("campaigns/bookmark-launch", "completed", "Draft exported for review")
```

States: `not_started`, `in_progress`, `completed`, `blocked`. Approval and an existing handoff package are required. This updates only the handoff manifest, timestamps and notes; it does not publish or enable publishing.


CLI usage:
```bash
genforge-marketing radar campaign-production-status --campaign campaigns/bookmark-launch --status completed --notes "Draft exported"
```
