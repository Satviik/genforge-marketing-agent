# Screening Agent → Trend Radar Integration

## Purpose

Keep the two repositories decoupled. The Screening Agent collects social content and exports a stable JSON snapshot. The Marketing Agent imports that snapshot, validates it into opportunity models, and ranks it in Trend Radar.

## Workflow

1. Run collection in the Screening Agent as configured.
2. Export a JSON snapshot:
   `genforge export --output output/screening-export.json`
3. Copy the export into the Marketing Agent workspace.
4. Import and rank it:
   `genforge-marketing radar import-screening --input output/screening-export.json`
5. Inspect `output/screening-radar-report.json`.

## Data boundaries

The integration preserves source topic, platform, URL, observed time, summary and available engagement counts. It does not fabricate saves, follower counts, duration, or missing measurements. The report score is a heuristic and a single snapshot cannot demonstrate velocity or causality.

## Future work

- Persist imported signals in the Radar database with stable source IDs.
- Add repeat-import deduplication and snapshot history.
- Calculate trend velocity only when multiple dated observations exist.
- Add Creative DNA analysis with explicit human review and evidence links.
