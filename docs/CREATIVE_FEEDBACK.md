# Creative Performance Feedback

Record manual performance snapshots for each creative. Metrics include views, reach, watch time, engagement, shares, saves, profile visits, inquiries, orders, and revenue. The local SQLite tracker computes descriptive rates and keeps snapshots for later comparison. It does not scrape social accounts, predict virality, or claim causal learning.

## Record a snapshot

```bash
genforge-marketing radar feedback-log --creative-id reel-001 --platform Instagram --metrics output/reel-metrics.json --tags output/reel-tags.json
```

The metrics and tags are JSON objects. Supported metric keys: `views`, `reach`, `watch_time_seconds`, `likes`, `comments`, `shares`, `saves`, `profile_visits`, `inquiries`, `orders`, `revenue_inr`.

## Report

```bash
genforge-marketing radar feedback-report --creative-id reel-001 --output output/feedback-report.json
```

Omit `--creative-id` to report all tracked creatives. Compare snapshots at similar post ages; observed rates are descriptive, not causal.
