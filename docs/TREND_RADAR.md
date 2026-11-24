# Trend Radar (initial local-fixture version)

Trend Radar provides a provider-neutral data model for trend signals, transparent scoring, reference storage, and report generation. This first iteration does **not** fetch Instagram/TikTok/YouTube data live.

## Input fixture

A JSON array of TrendSignal objects can be passed to `radar scan` or `radar report`. Fields include title, platform, URL, creator, publication/collection dates, view/like/comment/share/save counts, follower count, duration, category, notes, and completeness.

## Score

Signals are scored from available inputs. Engagement (35%), relative reach (25%), recency (20%), and completeness (20%) are normalized and missing metric components are excluded; remaining weights are renormalized. This is a heuristic rank—not a prediction of reach or virality. Single snapshots cannot establish growth velocity.

## Creative reference library

A reference combines a signal with a validated CreativeDNA record. The CLI stores these records in SQLite. Creative DNA is supplied as analysis notes; the command does not claim to have watched a URL or video.

## Commands

```shell
genforge-marketing radar scan --fixture data/trend-fixture.json --category desk-setup
genforge-marketing radar report --fixture data/trend-fixture.json
genforge-marketing radar analyze-reference --signal data/reference-signal.json --dna data/reference-dna.json
genforge-marketing radar references
genforge-marketing radar references --show ref-id
```

JSON reports include ranked scores, component breakdown, confidence (the weight coverage available), and explicit limitations.

## Creative Intelligence pattern summary

Summarize recurring Creative DNA across the reference library with:

```shell
genforge-marketing radar creative-patterns --store data/radar.sqlite --output output/creative-patterns.json
```

The summary ranks observed frequency for hook types, payoff types, visual patterns, editing patterns, psychological triggers, and adaptable principles. Counts are based on stored user/AI supplied analysis notes, not independent video analysis or performance causality.

## Product Radar

Product candidates can be ranked with `radar rank-products --input candidates.json`. Each candidate supports concept, trend association, printability (0-1), material grams, print hours, material cost per gram, selling price, personalization (0-1), demand score (0-1), competition (low/medium/high/unknown), and evidence notes.

The engine estimates material cost and gross profit after material only when enough inputs are present. It ranks candidates using weighted demand (30%), printability (25%), margin (20%), personalization (15%), and competition (10%). Missing margin or competition inputs are omitted and remaining weights are renormalized. These are screening scores, not market forecasts. Validate all assumptions before production.
