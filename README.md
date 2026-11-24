# GenForge Marketing Agent

A modular marketing planning and operations system for GenForge, including trend intelligence, content planning, strategy, and approval-first workflows.

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

## Content studio\n\nAfter creating a monthly plan JSON file, generate structured creative drafts with `genforge-marketing create-content genforge-business.json output/content-plan.json --output output/content-drafts.json`. The output includes carousel slide plans and Reel scene scripts, with fact-check notes. It does not generate final image/video files or publish anything; visual prompts are prepared for a future creative-tool integration.\n\n## Monthly strategy\n\nCreate a local, deterministic strategy with `genforge-marketing strategy genforge-business.json --year 2026 --month 12`. To use a chat-completions compatible model, set `GENFORGE_MARKETING_AI_PROVIDER=openai`, `GENFORGE_MARKETING_AI_API_KEY`, `GENFORGE_MARKETING_AI_MODEL`, and optionally `GENFORGE_MARKETING_AI_BASE_URL` in `.env`. The default `none` mode uses the local strategy engine. Both modes validate the structured strategy and keep it in draft status.\n\n## GitHub skill research\n\nRun `genforge-marketing research-skills --query "instagram marketing MCP"` to discover and assess public repositories. The command saves a JSON catalogue and never clones, installs, or executes repository code. Set `GENFORGE_MARKETING_GITHUB_TOKEN` in `.env` to improve API rate limits.\n\n## Safety

Publishing remains disabled by default. Scheduled events may prepare content and notify the owner, but must never bypass explicit approval. GitHub repositories are assessed before use; repository code is not installed or executed automatically.

## Trend Radar — initial version

The local-fixture Trend Radar scores trend signals transparently and stores creative references with structured Creative DNA notes. It does not yet connect to social platforms live or claim to analyze videos it cannot access.

Try the demo fixture:

```shell
genforge-marketing radar scan --fixture data/trend-radar-demo-fixture.json
genforge-marketing radar report --fixture data/trend-radar-demo-fixture.json
```

Read [Trend Radar documentation](docs/TREND_RADAR.md) for input schema, scoring, reference-library commands, and limitations.


## Screening Agent import

Export collected trend candidates from the Screening Agent and import them into Trend Radar:

```shell
# In the gen-forge-screening-agent environment/repository
genforge export --output output/screening-export.json

# In the marketing-agent repository
genforge-marketing radar import-screening --input output/screening-export.json
```

The import command validates the Screening Agent export through the shared integration adapter, ranks available snapshots, and writes a JSON report. It does not scrape new data or imply trend velocity from one snapshot.


## Persistent trend history

Record signals into a local SQLite history store from Python:

```python
from pathlib import Path
from genforge_marketing.intelligence.radar import load_fixture
from genforge_marketing.intelligence.trend_history import TrendHistoryStore
store = TrendHistoryStore(Path("data/trend-history.sqlite"))
for signal in load_fixture(Path("data/trend-radar-demo-fixture.json")):
    signal_id = store.record(signal)
    print(signal_id)
```

Compare stored observations with `genforge-marketing radar compare <signal-id>`. A comparison requires at least two snapshots at distinct times; reported velocity is descriptive change per day, not a prediction. SQLite is local and is not synchronized across machines.
