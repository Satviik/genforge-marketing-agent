# GenForge Marketing Agent

A modular marketing planning and operations system for GenForge. The first implementation milestone builds the screenshot requirements independently; integration with the existing Instagram screening CLI is deliberately deferred until the marketing system is ready.

## Scope being built

- Structured GenForge business profile and product catalogue.
- GitHub skill/MCP repository research with evidence-based reputation and license checks (`research-skills`).
- Monthly content planning for static posts and Reels.
- A five-pillar strategy engine with optional OpenAI-compatible model generation and validated structured output.
- Excel export with exactly two planning worksheets: `Posts` and `Reels`.
- Content production adapters for AI and MCP tools.
- Structured first-draft Instagram carousel and Reel content, including slide plans, hooks, scenes, captions, hashtags, CTAs and visual prompts.
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
genforge-marketing init-profile
genforge-marketing research-skills --query "instagram marketing MCP" --limit 10
genforge-marketing plan-month genforge-business.json --year 2026 --month 12 --posts 8 --reels 8
```

## Content studio\n\nAfter creating a monthly plan JSON file, generate structured creative drafts with `genforge-marketing create-content genforge-business.json output/content-plan.json --output output/content-drafts.json`. The output includes carousel slide plans and Reel scene scripts, with fact-check notes. It does not generate final image/video files or publish anything; visual prompts are prepared for a future creative-tool integration.\n\n## Monthly strategy\n\nCreate a local, deterministic strategy with `genforge-marketing strategy genforge-business.json --year 2026 --month 12`. To use a chat-completions compatible model, set `GENFORGE_MARKETING_AI_PROVIDER=openai`, `GENFORGE_MARKETING_AI_API_KEY`, `GENFORGE_MARKETING_AI_MODEL`, and optionally `GENFORGE_MARKETING_AI_BASE_URL` in `.env`. The default `none` mode uses the local strategy engine. Both modes validate the structured strategy and keep it in draft status.\n\n## GitHub skill research\n\nRun `genforge-marketing research-skills --query "instagram marketing MCP"` to discover and assess public repositories. The command saves a JSON catalogue and never clones, installs, or executes repository code. Set `GENFORGE_MARKETING_GITHUB_TOKEN` in `.env` to improve API rate limits.\n\n## Integration boundary

Do not connect this repository to `gen-forge-screening-agent` while the planning, workbook, skill research, content production, approval, publishing and analytics milestones are still being built. Until then, research/trend inputs can be entered manually or loaded from fixtures. The CLI connection is the final integration milestone.

## Safety

Publishing remains disabled by default. Scheduled events may prepare content and notify the owner, but must never bypass explicit approval. GitHub repositories are assessed before use; repository code is not installed or executed automatically.

## Trend Radar — initial version

The local-fixture Trend Radar scores trend signals transparently and stores creative references with structured Creative DNA notes. It does not yet connect to social platforms live or claim to analyze videos it cannot access.

Try the demo fixture:

```shell
genforge-marketing radar scan --fixture data/trend-radar-demo-fixture.json
genforge-marketing radar report --fixture data/trend-radar-demo-fixture.json
```

Read [Trend Radar documentation](docs/TREND_RADAR.md) for input schema, scoring, reference-library commands, and limitations.
