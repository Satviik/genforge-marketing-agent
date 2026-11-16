# GenForge Marketing Agent

A modular marketing planning and operations system for GenForge. The first implementation milestone builds the screenshot requirements independently; integration with the existing Instagram screening CLI is deliberately deferred until the marketing system is ready.

## Scope being built

- Structured GenForge business profile and product catalogue.
- GitHub skill/MCP repository research with evidence-based reputation and license checks.
- Monthly content planning for static posts and Reels.
- Excel export with exactly two planning worksheets: `Posts` and `Reels`.
- Content production adapters for AI and MCP tools.
- Approval queue and scheduled workflow triggers.
- Publishing adapter with a hard human-approval gate.
- Analytics capture and feedback for future plans.

## Architecture and requirements

See [Product Requirements](docs/PRODUCT_REQUIREMENTS.md) and [Architecture](docs/ARCHITECTURE.md).

## Development setup

Requires Python 3.12+.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
```

## Integration boundary

Do not connect this repository to `gen-forge-screening-agent` while the planning, workbook, skill research, content production, approval, publishing and analytics milestones are still being built. Until then, research/trend inputs can be entered manually or loaded from fixtures. The CLI connection is the final integration milestone.

## Safety

Publishing remains disabled by default. Scheduled events may prepare content and notify the owner, but must never bypass explicit approval. GitHub repositories are assessed before use; repository code is not installed or executed automatically.
