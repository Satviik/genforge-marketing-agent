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

The import command validates the Screening Agent export through the shared integration adapter, ranks available snapshots, writes a JSON report, and automatically records each imported signal in the local SQLite history store. The report includes stable signal IDs for future comparison. You can override the database path with `--history-store`.

```shell
genforge-marketing radar import-screening --input output/screening-export.json --history-store data/trend-history.sqlite
genforge-marketing radar compare trend-<stable-id> --store data/trend-history.sqlite
```

Repeated imports create historical observations (same signal and observation timestamp replaces that row); trend velocity is available only after distinct observations and is descriptive, not predictive.


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

## Creative Intelligence pattern summaries

Aggregate recurring Creative DNA fields across saved references:

```shell
genforge-marketing radar creative-patterns --store data/radar.sqlite --output output/creative-patterns.json
```

This summarizes hook types, payoffs, visual patterns, editing patterns, psychological triggers, and adaptable principles by frequency. It counts supplied notes only; it does not infer causality or guarantee performance.


## Product Radar (candidate screening)

Rank product concepts using demand, printability, estimated material margin, personalization potential, competition, and print-time efficiency inputs:

```shell
genforge-marketing radar rank-products --input data/product-candidates.json --output output/product-radar.json
```

Example candidate input (JSON array):

```json
[{
  "name": "Personalized desk organizer",
  "trend": "#desksetup",
  "concept": "Modular organizer with custom name plate",
  "printability": 0.9,
  "estimated_material_grams": 80,
  "estimated_print_hours": 4.5,
  "material_cost_per_gram": 1.8,
  "selling_price": 399,
  "personalization_score": 0.9,
  "demand_score": 0.7,
  "competition": "medium",
  "evidence_notes": "Replace estimates with actual local data before ranking."
}]
```

Material estimates exclude electricity, machine wear, failed prints, labor, packaging, delivery and fees. Scores are transparent heuristics, not market predictions.
