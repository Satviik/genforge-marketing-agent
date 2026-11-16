# Architecture

```text
Business Profile ─────┐
Manual Trend Research ├──> Planning Engine ──> Monthly Content Plan
GitHub Skill Catalog ┘                              │
                                                    ├──> Excel: Posts
                                                    └──> Excel: Reels
                                                             │
                                                    Human edits / approval
                                                             │
                                                    Content Production
                                                    (AI + MCP adapters)
                                                             │
                                                    Approval Queue
                                                             │
                                             Calendar Trigger / Scheduler
                                                             │
                                      Instagram Publishing Adapter (later)
                                                             │
                                               Published Content Metrics
                                                             │
                                                   Analytics / Learning

Future input: GenForge Screening CLI ──> Trend Research
```

## Boundaries
- profile: business facts and brand constraints.
- research: GitHub repository discovery and evidence-based skill evaluation.
- planning: content calendar and post/Reel brief generation.
- workbook: Excel export/import contract.
- production: AI provider and MCP tool interfaces; no provider assumed.
- workflow: approval states and event/trigger contracts.
- publishing: platform adapter boundary; disabled until a supported API and approval process exist.
- analytics: normalized performance records and plan feedback.

The marketing agent owns planning and workflow state. The screening CLI remains independent. They connect only in the final integration milestone.
