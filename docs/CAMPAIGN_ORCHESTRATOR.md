# Campaign Orchestrator (workflow status MVP)

The orchestrator tracks campaign progress in the campaign manifest and reports the next incomplete stage. It does not execute production or publish automatically.

## Lifecycle stages and prerequisites

Stages: research, analysis, brief, storyboard, production, review, published, metrics, learning.

Advancing a stage to `in_progress`, `completed`, `approved`, or `skipped` requires its prerequisite stages to be completed, approved, or explicitly skipped:

| Stage | Prerequisite |
|---|---|
| research | none |
| analysis | research |
| brief | analysis |
| storyboard | brief |
| production | storyboard |
| review | production |
| published | review |
| metrics | published |
| learning | metrics |

A stage can be set back to `pending` or `blocked` without prerequisite validation, allowing corrections and resets. Explicitly skipping a stage satisfies it for subsequent progression.

Publishing remains protected by a separate human approval gate: the campaign must have an approved review record and status `approved_for_production`. Publishing is not automated.

## CLI

```bash
genforge-marketing radar campaign-status --campaign campaigns/bookmark-launch
genforge-marketing radar campaign-stage --campaign campaigns/bookmark-launch/campaign.json --stage research --status completed --note "Research reviewed"
```
