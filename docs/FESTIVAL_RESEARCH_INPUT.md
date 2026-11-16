# Festival and Seasonal Research Input

## Purpose

The monthly planner accepts an explicit occasion calendar for the requested
month. This first implementation supports manually researched or team-supplied
festival and seasonal occasions. It does not guess festival dates or silently
treat model suggestions as verified facts.

## JSON contract

Example:

```json
{
  "year": 2026,
  "month": 11,
  "market": "India",
  "occasions": [
    {
      "name": "Diwali",
      "date": "2026-11-08",
      "market": "India",
      "confidence": "verified",
      "source_name": "Official calendar",
      "source_url": "https://example.org/calendar",
      "campaign_notes": "Consider gifting and festive product bundles."
    },
    {
      "name": "Winter gifting season",
      "date": "2026-11-20",
      "market": "India",
      "confidence": "suggested",
      "campaign_notes": "Explore personalized gifting ideas."
    }
  ]
}
```

The example dates and source are illustrative only; they are not asserted as
correct dates for a real festival.

## Validation rules

- The calendar has one explicit year, month and market.
- Every occasion date must fall within that requested month.
- Every occasion market must match the calendar market.
- An occasion marked `verified` must include a source name or source URL.
- An occasion marked `suggested` may omit a source and must remain visibly
  identified as a suggestion in downstream planning.
- The planner must not invent prices, offers, stock, product capabilities or
  festival dates.

## Next integration steps

1. Expose occasion-calendar input through the MCP planning tool.
2. Add a research adapter that returns source-backed candidate occasions.
3. Let the user/team member confirm candidates before treating them as verified.
4. Pass confirmed occasions into the content strategy and Posts/Reels workbook.
5. Preserve existing approved and published content during plan revisions.
