# GenForge Marketing Agent

An AI-assisted marketing operations layer for GenForge. It turns product and trend signals into a reviewable marketing workflow: research, content planning, draft generation, publishing integrations, and performance feedback.

## Design principles

- **Human approval first:** generated content is reviewed before publishing.
- **Provider-agnostic:** social networks and AI providers sit behind adapters.
- **Reuse existing intelligence:** consume trend data from `gen-forge-screening-agent`; do not duplicate its collection logic.
- **Safe by default:** credentials stay in environment variables and are never committed.
- **Incremental delivery:** begin with a reliable local workflow before adding autonomous scheduling or publishing.

## Planned workflow

1. Read trend/product signals from the screening CLI through a stable JSON contract.
2. Rank opportunities for GenForge using relevance, audience fit, and evidence.
3. Build a content brief (platform, audience, angle, format, CTA).
4. Generate editable captions and creative direction.
5. Store drafts with explicit review status.
6. Add publishing adapters only after account permissions and platform constraints are configured.
7. Ingest performance metrics and feed learnings back into planning.

## Quick start

Requires Python 3.12+.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
copy .env.example .env
genforge-marketing --help
pytest
```

On macOS/Linux, activate with `source .venv/bin/activate`.

## Configuration

Copy `.env.example` to `.env`. Never commit real API keys or account credentials.\n\nFor direct CLI synchronization, install `genforge-screening-agent` in the same Python environment and set `GENFORGE_MARKETING_SCREENING_WORKDIR` to the local screening repository folder. The example assumes both repositories are sibling folders; the screening process runs from that folder so it reads the existing `genforge.db` file.

## Current status

Phase 1 foundation: configuration, typed models, a local CLI, a JSON handoff contract for the screening agent, and tests. Publishing integrations and autonomous execution are intentionally not enabled yet.
