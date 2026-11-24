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

## Campaign dashboard

View campaign progress, missing deliverables and quality checks in one report:

```bash
genforge-marketing radar campaign-dashboard --campaign campaigns/bookmark-launch --output output/campaign-dashboard.json
```

See [Campaign Dashboard](docs/CAMPAIGN_DASHBOARD.md). This is read-only.

## Campaign quality gate

Validate campaign creative files before review:

```bash
genforge-marketing radar campaign-quality-gate --campaign campaigns/bookmark-launch --output output/quality-gate.json
```

See [Campaign Quality Gate](docs/CAMPAIGN_QUALITY_GATE.md). Passing checks never auto-approve or publish.

## Campaign creative pipeline

Generate an original brief and storyboard directly into a campaign workspace:

```bash
genforge-marketing radar campaign-build-creative --campaign campaigns/bookmark-launch --duration 20
```

See [Campaign Creative Pipeline](docs/CAMPAIGN_PIPELINE.md). The command registers artifacts and sets the brief stage to `in_progress`; it never overwrites files.

## Campaign stage starter

Create the next stage's editable starter file without overwriting existing work:

```bash
genforge-marketing radar campaign-start-stage --campaign campaigns/bookmark-launch
genforge-marketing radar campaign-start-stage --campaign campaigns/bookmark-launch --stage brief
```

See [Campaign Stage Task](docs/CAMPAIGN_STAGE_TASK.md). This creates a template only and does not update campaign stage status.

## Campaign execution planner

Get a deterministic next-step recommendation from campaign progress and missing declared deliverables:

```bash
genforge-marketing radar campaign-plan --campaign campaigns/bookmark-launch --output output/campaign-plan.json
```

See [Campaign Execution Plan](docs/CAMPAIGN_EXECUTION_PLAN.md). It is advisory only and never runs production or publishing actions.

## Campaign artifact audit

Declare expected deliverables in the campaign manifest under `artifacts`, then check them:

```bash
genforge-marketing radar campaign-audit --campaign campaigns/bookmark-launch
```

See [Campaign Artifact Audit](docs/CAMPAIGN_ARTIFACT_AUDIT.md). It checks file presence only and never auto-completes stages.

## Campaign orchestrator

Track progress and update campaign stages:

```bash
genforge-marketing radar campaign-status --campaign campaigns/bookmark-launch
genforge-marketing radar campaign-stage --campaign campaigns/bookmark-launch/campaign.json --stage research --status completed --note "Research reviewed"
```

See [Campaign Orchestrator](docs/CAMPAIGN_ORCHESTRATOR.md). This tracks workflow status; it does not automatically publish.

## Campaign workspace

Initialize a local folder structure for an individual campaign:

```bash
genforge-marketing radar campaign-init --name "Bookmark launch" --product "Custom bookmark" --objective inquiries --audience "book lovers" --root campaigns
```

Creates folders for references, observations, drafts, production, published records, metrics and experiments, with a campaign manifest and experiment template. See [Campaign Workspace](docs/CAMPAIGN_WORKSPACE.md).

## Creative experiments

Compare variants from an experiment spec with latest feedback metrics:

```bash
genforge-marketing radar experiment-report --experiment experiments/hook-01.json --feedback output/creative-feedback-report.json --output output/hook-01-report.json
```

See [Creative Experiments](docs/CREATIVE_EXPERIMENTS.md). Results are descriptive and not causal.

## Campaign pack (one-step workflow)

Generate the original brief and Claude handoff together:

```bash
genforge-marketing radar campaign-pack --product "Custom bookmark" --description "Personalized gift" --objective inquiries --duration 20 --breakdown output/creative-breakdown.json --timeline output/reel-timeline.json --visual-notes output/frame-visual-notes.json --brief-output output/campaign-brief.json --handoff-output output/claude-handoff.md
```

Optional evidence files can be omitted. This assembles both outputs locally and calls no external model. See [Campaign Pack](docs/CAMPAIGN_PACK.md).

## Creative insights

Generate exploratory comparisons and follow-up test ideas from feedback reports:

```bash
genforge-marketing radar creative-insights --report output/creative-feedback-report.json --output output/creative-insights.json
```

This ranks observed metrics and suggests controlled experiments. It does not claim causality or statistical significance. See [Creative Insights](docs/CREATIVE_INSIGHTS.md).

## Creative performance feedback

Track manually entered results for published creatives and generate descriptive reports:

```bash
genforge-marketing radar feedback-log --creative-id reel-001 --platform Instagram --metrics output/reel-metrics.json --tags output/reel-tags.json
genforge-marketing radar feedback-report --creative-id reel-001 --output output/feedback-report.json
```

Metrics can include views, reach, watch time, likes, comments, shares, saves, profile visits, inquiries, orders, and revenue. See [Creative Feedback](docs/CREATIVE_FEEDBACK.md). Reports are descriptive and do not infer causality.

## Claude handoff export

Export the generated brief plus optional breakdown, timeline, and visual observations into a Markdown package for Claude:

```bash
genforge-marketing radar export-claude --brief output/original-reel-brief.json --breakdown output/creative-breakdown.json --timeline output/reel-timeline.json --visual-notes output/frame-visual-notes.json --output output/claude-creative-handoff.md
```

The export contains a structured production prompt, product/campaign context, creative plan, reference adaptation evidence, and originality/review guardrails. It does not call Claude or any paid model. See [Claude Handoff](docs/CLAUDE_HANDOFF.md).

## Original creative generator

Generate a structured, original Reel brief locally from product details and optional reference mechanics:

```bash
genforge-marketing radar generate-creative --product "Custom bookmark" --description "Personalized 3D printed bookmark" --objective inquiries --audience "book lovers and gift buyers" --duration 20 --breakdown output/creative-breakdown.json --output output/original-reel-brief.json
```

This deterministic starter creates concept and hook options, timed scenes, shot/edit direction, captions, CTAs and adaptation notes. It calls no AI model or paid API. See [Original Creative Generator](docs/ORIGINAL_CREATIVE_GENERATOR.md).

## Creative breakdown

Combine the reconstructed timeline and optional manual frame observations into a reusable structure:

```bash
genforge-marketing radar creative-breakdown --timeline output/reel-timeline.json --visual-notes output/frame-visual-notes.json --output output/creative-breakdown.json
```

Outputs hook candidates, visual resets, process beats, pause/audio gaps, payoff candidates, and original-adaptation guidance. Labels are heuristic, not virality or retention claims. See [Creative Breakdown](docs/CREATIVE_BREAKDOWN.md).

## Frame visual notes

Create an editable per-frame observation sheet for visual reverse-engineering:

```bash
genforge-marketing radar visual-notes --media output/media-inspection.json --output output/frame-visual-notes.json
```

Annotate framing, angle, camera movement, subject, action, lighting, colors, text overlays, composition, transitions and a clearly labeled creative-purpose hypothesis. This is a manual template, not automated image understanding. See [Frame Visual Notes](docs/FRAME_VISUAL_NOTES.md).

## Reel storyboard

Create a local HTML storyboard to review the timeline with timestamps and sampled frame images:

```bash
genforge-marketing radar storyboard --timeline output/reel-timeline.json --frames-dir output/frames --output output/reel-storyboard.html
```

Open the generated HTML file in a browser. See [Storyboard documentation](docs/STORYBOARD.md).

## Reel timeline reconstruction

Combine sampled frames, detected scene changes, silence intervals and timestamped speech into one chronological JSON timeline:

```bash
genforge-marketing radar reconstruct-timeline --media output/media-inspection.json --scenes output/scene-changes.json --audio output/audio-inspection.json --transcript output/transcription.json --output output/reel-timeline.json
```

Each evidence source is optional, but provide at least one. Transcript role labels are simple heuristics and require review. See [Timeline reconstruction](docs/TIMELINE_RECONSTRUCTION.md).

## Local Reel audio transcription

Optional, free local transcription (no paid API). Install the extra:

```bash
pip install -e ".[transcription]"
```

After extracting audio with `radar inspect-audio`, transcribe with timestamps:

```bash
genforge-marketing radar transcribe-audio --input output/reel-audio.wav --output output/transcription.json --model base --device cpu --language en
```

The first run downloads Whisper model weights. See [Media inspection](docs/MEDIA_INSPECTION.md) for details and limitations.

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


## Creative Intelligence — reverse-engineering content structure

GenForge's Creative DNA library is designed to dissect **how** a Reel or post is constructed: first frame, hook, beat-by-beat timeline, retention devices, proof, payoff, CTA, carousel slide roles, caption structure, visual hierarchy, editing/audio patterns, and reusable principles. Study whole references and separate observation from hypothesis. Adapt mechanisms into original GenForge content rather than copying scripts or creators. See [Creative Intelligence methodology](docs/CREATIVE_INTELLIGENCE.md).


### Scene-change detection

Detect candidate visual changes and cut points locally:

```bash
genforge-marketing radar detect-scenes --input path/to/reel.mp4 --threshold 0.30 --output output/scene-changes.json
```

This uses FFmpeg's scene filter. It identifies visual-change candidates, not semantic story beats, and can be sensitive to camera motion or flashes.

### Audio extraction and silence detection

Extract audio locally and find pause intervals:

```bash
genforge-marketing radar inspect-audio --input path/to/reel.mp4 --audio-output output/reel-audio.wav --output output/audio-inspection.json --noise-db -35 --min-silence 0.35
```

The command exports mono 16 kHz WAV and reports threshold-based silence intervals. It does not transcribe speech. Details: [Media inspection](docs/MEDIA_INSPECTION.md).

## Local Media Inspection (first automated media pipeline)

Index a local video and sample frames without paid APIs:

```bash
genforge-marketing radar inspect-media --input path/to/reel.mp4 --output output/media-inspection.json --frames-dir output/media-frames --interval 2
```

Requires FFmpeg and FFprobe installed locally. It produces metadata and timestamped frame files for later analysis, but does not yet interpret frames, extract/transcribe audio, or detect scene changes. See [Local Media Inspection](docs/MEDIA_INSPECTION.md).

## Reel Autopsy (observations-first MVP)

Reconstruct a short-form content blueprint from supplied observations and timestamped beats:

```bash
genforge-marketing radar autopsy --input data/reel-reference.json --output output/reel-autopsy.json
```
This MVP does not download or inspect video, transcribe audio, or claim automated media analysis. It outputs a timeline, beat-role sequence, descriptive text statistics, evidence limitations, and a blank worksheet for adapting the mechanism into original GenForge content. See [Reel Autopsy docs](docs/REEL_AUTOPSY.md).
