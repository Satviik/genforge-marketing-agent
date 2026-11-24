"""Command-line interface for GenForge Marketing Agent."""

import json
from datetime import time
from pathlib import Path

import typer
from rich import print
from rich.table import Table

from genforge_marketing import __version__
from genforge_marketing.planning.generator import generate_monthly_plan
from genforge_marketing.profile.models import BusinessProfile
from genforge_marketing.research.github_client import GitHubResearchError, GitHubSkillResearcher
from genforge_marketing.config import get_settings
from genforge_marketing.content.studio import create_content_drafts
from genforge_marketing.planning.models import MonthlyContentPlan
from genforge_marketing.planning.occasions import OccasionCalendar
from genforge_marketing.strategy.engine import generate_strategy
from genforge_marketing.strategy.llm import OpenAICompatibleStrategyProvider, StrategyProviderError
from genforge_marketing.workbook.exporter import export_monthly_plan

app = typer.Typer(help="GenForge marketing planning and operations.")
radar_app = typer.Typer(help="Trend Radar and creative reference intelligence.")
app.add_typer(radar_app, name="radar")

from genforge_marketing.intelligence.radar import CreativeDNA, Reference, TrendSignal, ReferenceStore, build_report, load_fixture, score_signal


@app.command()
def version() -> None:
    """Show the installed package version."""
    print(f"GenForge Marketing Agent [bold cyan]v{__version__}[/bold cyan]")


@app.command("research-skills")
def research_skills(
    query: str = typer.Option(
        "instagram marketing OR social media content OR MCP server",
        "--query",
        "-q",
        help="GitHub repository search query.",
    ),
    limit: int = typer.Option(10, "--limit", "-n", min=1, max=30),
    output: Path = typer.Option(Path("data/github-skill-research.json"), "--output", "-o"),
) -> None:
    """Discover and assess GitHub marketing skills and MCP repositories."""
    settings = get_settings()
    try:
        with GitHubSkillResearcher(token=settings.github_token) as researcher:
            assessments = researcher.search(query=query, limit=limit)
    except (GitHubResearchError, ValueError) as exc:
        print(f"[red]GitHub research failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps([item.model_dump(mode="json") for item in assessments], indent=2),
        encoding="utf-8",
    )
    table = Table(title=f"GitHub skill research ({len(assessments)} repositories)")
    table.add_column("Repository")
    table.add_column("Score", justify="right")
    table.add_column("Recommendation")
    for item in sorted(assessments, key=lambda result: result.score, reverse=True):
        table.add_row(item.full_name, f"{item.score:.1f}", item.recommendation)
    print(table)
    print(f"[green]Research catalogue saved:[/green] {output}")
    print("[yellow]Research only: no repositories were cloned, installed or executed.[/yellow]")


@app.command("create-content")
def create_content(
    profile_file: Path = typer.Argument(..., exists=True, readable=True, dir_okay=False),
    plan_file: Path = typer.Argument(..., exists=True, readable=True, dir_okay=False),
    output: Path = typer.Option(Path("output/content-drafts.json"), "--output", "-o"),
) -> None:
    """Create first-draft post and Reel creative from a monthly plan."""
    try:
        profile = BusinessProfile.model_validate_json(profile_file.read_text(encoding="utf-8"))
        plan = MonthlyContentPlan.model_validate_json(plan_file.read_text(encoding="utf-8"))
        drafts = create_content_drafts(profile, plan)
    except (ValueError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(drafts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    table = Table(title="GenForge content studio")
    table.add_column("Format")
    table.add_column("Drafts", justify="right")
    table.add_row("Posts", str(len(drafts["posts"])))
    table.add_row("Reels", str(len(drafts["reels"])))
    print(table)
    print(f"[green]Creative drafts saved:[/green] {output}")
    print("[yellow]Drafts only. Review facts, images, music rights and copy before approval.[/yellow]")


@app.command("strategy")
def strategy(
    profile_file: Path = typer.Argument(..., exists=True, readable=True, dir_okay=False),
    year: int = typer.Option(..., "--year", min=2020, max=2100),
    month: int = typer.Option(..., "--month", min=1, max=12),
    output: Path = typer.Option(Path("output/monthly-strategy.json"), "--output", "-o"),
) -> None:
    """Generate a grounded monthly content strategy from the business profile."""
    settings = get_settings()
    try:
        profile = BusinessProfile.model_validate_json(profile_file.read_text(encoding="utf-8"))
        if settings.ai_provider.lower() in {"openai", "openai_compatible"}:
            if not settings.ai_api_key or not settings.ai_model:
                raise ValueError(
                    "AI provider is enabled but GENFORGE_MARKETING_AI_API_KEY or "
                    "GENFORGE_MARKETING_AI_MODEL is missing."
                )
            result = OpenAICompatibleStrategyProvider(
                api_key=settings.ai_api_key,
                model=settings.ai_model,
                base_url=settings.ai_base_url,
            ).generate(profile, year, month)
            provider_label = f"AI provider: {settings.ai_provider} / {settings.ai_model}"
        else:
            result = generate_strategy(profile, year, month)
            provider_label = "Strategy mode: local deterministic fallback"
    except (ValueError, json.JSONDecodeError, StrategyProviderError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(f"[bold cyan]{result.business_name} — {year}-{month:02d} strategy[/bold cyan]")
    print(provider_label)
    print(f"Primary goal: {result.primary_goal}")
    print(f"Positioning: {result.positioning_summary}")
    table = Table(title="Content pillars")
    table.add_column("Pillar")
    table.add_column("Share", justify="right")
    table.add_column("Purpose")
    for pillar in result.pillars:
        table.add_row(pillar.name, f"{pillar.recommended_share:.0%}", pillar.purpose)
    print(table)
    if result.assumptions:
        print("[yellow]Profile gaps to complete:[/yellow]")
        for assumption in result.assumptions:
            print(f" • {assumption}")
    print(f"[green]Strategy saved:[/green] {output}")
    print("[yellow]Strategy is a draft; review before using it as a publishing plan.[/yellow]")


@app.command("init-profile")
def init_profile(
    output: Path = typer.Option(Path("genforge-business.json"), "--output", "-o"),
) -> None:
    """Create an editable GenForge business profile template."""
    if output.exists():
        raise typer.BadParameter(f"{output} already exists; choose another path to avoid overwriting.")
    output.parent.mkdir(parents=True, exist_ok=True)
    profile = BusinessProfile()
    output.write_text(profile.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(f"[green]Business profile template created:[/green] {output}")
    print("Edit the products, target audiences, brand voice and constraints before planning.")


@app.command("plan-month")
def plan_month(
    profile_file: Path = typer.Argument(..., exists=True, readable=True, dir_okay=False),
    year: int = typer.Option(..., "--year", min=2020, max=2100),
    month: int = typer.Option(..., "--month", min=1, max=12),
    posts: int = typer.Option(8, "--posts", min=0, max=31),
    reels: int = typer.Option(8, "--reels", min=0, max=31),
    post_time: str = typer.Option("19:00", "--post-time"),
    reel_time: str = typer.Option("18:30", "--reel-time"),
    occasions_file: Path | None = typer.Option(
        None, "--occasions", help="JSON file with researched festival/seasonal occasions."
    ),
    output: Path = typer.Option(Path("output/content-plan.xlsx"), "--output", "-o"),
) -> None:
    """Generate a monthly draft calendar and a two-sheet Excel workbook."""
    try:
        profile = BusinessProfile.model_validate_json(profile_file.read_text(encoding="utf-8"))
        occasion_calendar = (
            OccasionCalendar.model_validate_json(occasions_file.read_text(encoding="utf-8"))
            if occasions_file
            else None
        )
        plan = generate_monthly_plan(
            profile=profile,
            year=year,
            month=month,
            post_count=posts,
            reel_count=reels,
            post_time=time.fromisoformat(post_time),
            reel_time=time.fromisoformat(reel_time),
            occasion_calendar=occasion_calendar,
        )
    except (ValueError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    workbook_path = export_monthly_plan(plan, output)
    json_path = output.with_suffix(".json")
    json_path.write_text(plan.model_dump_json(indent=2) + "\n", encoding="utf-8")

    table = Table(title=f"GenForge content plan — {year}-{month:02d}")
    table.add_column("Format")
    table.add_column("Items", justify="right")
    table.add_row("Posts", str(len(plan.posts)))
    table.add_row("Reels", str(len(plan.reels)))
    print(table)
    print(f"[green]Excel workbook:[/green] {workbook_path}")
    print(f"[green]Editable plan data:[/green] {json_path}")
    print("[yellow]All items are drafts. Nothing has been published.[/yellow]")



@radar_app.command("inspect-audio")
def radar_inspect_audio(
    input_file: Path = typer.Option(..., "--input", exists=True, readable=True, dir_okay=False, help="Local video file."),
    audio_output: Path = typer.Option(Path("output/extracted-audio.wav"), "--audio-output", help="Extracted WAV destination."),
    output: Path = typer.Option(Path("output/audio-inspection.json"), "--output", "-o"),
    noise_db: float = typer.Option(-35.0, "--noise-db", help="Silence detection threshold in dB (<=0)."),
    min_silence: float = typer.Option(0.35, "--min-silence", min=0.01, help="Minimum silence duration in seconds."),
) -> None:
    """Extract audio and detect silence locally; does not transcribe speech."""
    from genforge_marketing.intelligence.media_inspector import MediaInspectionError
    from genforge_marketing.intelligence.audio_inspector import extract_audio_and_detect_silence

    try:
        report = extract_audio_and_detect_silence(input_file, audio_output, noise_db, min_silence)
    except (MediaInspectionError, ValueError, FileNotFoundError) as exc:
        print("[red]Audio inspection failed:[/red]", exc)
        raise typer.Exit(code=1) from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[green]Audio inspection saved:[/green] {output}")
    print(f"Silence intervals: {report['silence_detection']['interval_count']}")
    print(f"Extracted WAV: {audio_output}")
    print("[yellow]Audio extracted and silence indexed; speech transcription was not performed.[/yellow]")


@radar_app.command("reconstruct-timeline")
def radar_reconstruct_timeline(
    media_report: Path | None = typer.Option(None, "--media", help="JSON output from inspect-media."),
    scene_report: Path | None = typer.Option(None, "--scenes", help="JSON output from detect-scenes."),
    audio_report: Path | None = typer.Option(None, "--audio", help="JSON output from inspect-audio."),
    transcript_report: Path | None = typer.Option(None, "--transcript", help="JSON output from transcribe-audio."),
    output: Path = typer.Option(Path("output/reel-timeline.json"), "--output", "-o"),
) -> None:
    """Merge local frame, scene, silence and transcript reports into one timeline."""
    sources = [media_report, scene_report, audio_report, transcript_report]
    if not any(sources):
        raise typer.BadParameter("Provide at least one source report using --media, --scenes, --audio, or --transcript.")
    def load_json(path: Path | None) -> dict:
        if path is None:
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            raise typer.BadParameter(f"Cannot read JSON report {path}: {exc}") from exc
    from genforge_marketing.intelligence.timeline_reconstruction import reconstruct_timeline
    report = reconstruct_timeline(load_json(media_report), load_json(scene_report), load_json(audio_report), load_json(transcript_report))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[green]Reconstructed timeline saved:[/green] {output}")
    print(f"Events: {report['event_count']}")
    summary = report["evidence_summary"]
    print(f"Frames: {summary['sampled_frames']} | Scene changes: {summary['scene_changes']} | Silences: {summary['silence_intervals']} | Transcript segments: {summary['transcript_segments']}")
    print("[yellow]Timeline labels are evidence-based heuristics; verify hook, process, and payoff manually.[/yellow]")


@radar_app.command("creative-breakdown")
def radar_creative_breakdown(
    timeline_file: Path = typer.Option(..., "--timeline", exists=True, readable=True, dir_okay=False),
    visual_notes_file: Path | None = typer.Option(None, "--visual-notes", exists=True, readable=True, dir_okay=False),
    output: Path = typer.Option(Path("output/creative-breakdown.json"), "--output", "-o"),
) -> None:
    """Build a reusable creative structure report from timeline and optional frame notes."""
    from genforge_marketing.intelligence.creative_breakdown import build_creative_breakdown
    try:
        timeline = json.loads(timeline_file.read_text(encoding="utf-8"))
        notes = json.loads(visual_notes_file.read_text(encoding="utf-8")) if visual_notes_file else {}
        report = build_creative_breakdown(timeline, notes)
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(f"Could not build creative breakdown: {exc}") from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[green]Creative breakdown saved:[/green] {output}")
    print(f"Phases: {len(report['phases'])} | Confidence: {report['confidence']}")
    print("[yellow]Structure labels are heuristic; adapt mechanics only, not source content.[/yellow]")


@radar_app.command("generate-creative")
def radar_generate_creative(
    product: str = typer.Option(..., "--product", help="Product name."),
    description: str = typer.Option("", "--description", help="Product description or benefit."),
    objective: str = typer.Option("awareness", "--objective", help="Campaign objective."),
    audience: str = typer.Option("people interested in custom 3D printed products", "--audience"),
    platform: str = typer.Option("Instagram Reels", "--platform"),
    duration: int = typer.Option(20, "--duration", min=8, max=90, help="Reel duration in seconds."),
    brand_voice: str = typer.Option("creative, helpful, maker-focused", "--brand-voice"),
    breakdown_file: Path | None = typer.Option(None, "--breakdown", exists=True, readable=True, dir_okay=False, help="Optional creative-breakdown JSON."),
    output: Path = typer.Option(Path("output/original-reel-brief.json"), "--output", "-o"),
) -> None:
    """Generate an original, local creative brief from product details and optional reference mechanics."""
    from genforge_marketing.intelligence.creative_generator import generate_original_reel
    try:
        breakdown = json.loads(breakdown_file.read_text(encoding="utf-8")) if breakdown_file else {}
        brief = generate_original_reel(product, description, objective, audience, platform, duration, brand_voice, breakdown)
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(f"Could not generate creative brief: {exc}") from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(brief, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[green]Original creative brief saved:[/green] {output}")
    print(f"Scenes: {len(brief['production_plan']['scenes'])} | Duration: {duration}s")
    print("[yellow]Local deterministic draft only; review before production. No AI API was called.[/yellow]")


@radar_app.command("export-claude")
def radar_export_claude(
    brief_file: Path = typer.Option(..., "--brief", exists=True, readable=True, dir_okay=False, help="Original creative brief JSON."),
    breakdown_file: Path | None = typer.Option(None, "--breakdown", exists=True, readable=True, dir_okay=False),
    timeline_file: Path | None = typer.Option(None, "--timeline", exists=True, readable=True, dir_okay=False),
    visual_notes_file: Path | None = typer.Option(None, "--visual-notes", exists=True, readable=True, dir_okay=False),
    output: Path = typer.Option(Path("output/claude-creative-handoff.md"), "--output", "-o"),
) -> None:
    """Export the creative brief and optional evidence reports as a Claude-ready Markdown package."""
    from genforge_marketing.intelligence.claude_handoff import export_claude_package
    try:
        destination = export_claude_package(brief_file, output, breakdown_file, timeline_file, visual_notes_file)
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(f"Could not export Claude handoff: {exc}") from exc
    print(f"[green]Claude handoff package exported:[/green] {destination}")
    print("[yellow]Review the Markdown package before sharing; this command calls no external model.[/yellow]")


@radar_app.command("feedback-log")
def radar_feedback_log(
    creative_id: str = typer.Option(..., "--creative-id"),
    platform: str = typer.Option("Instagram", "--platform"),
    metrics_file: Path = typer.Option(..., "--metrics", exists=True, readable=True, dir_okay=False, help="JSON object of metrics."),
    tags_file: Path | None = typer.Option(None, "--tags", exists=True, readable=True, dir_okay=False, help="Optional JSON object of creative tags."),
    store_path: Path = typer.Option(Path("data/creative-feedback.sqlite"), "--store"),
) -> None:
    """Record a manual performance snapshot for a creative."""
    from genforge_marketing.intelligence.creative_feedback import CreativeFeedbackStore
    try:
        metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
        tags = json.loads(tags_file.read_text(encoding="utf-8")) if tags_file else {}
        row_id = CreativeFeedbackStore(store_path).record(creative_id, platform, metrics, tags)
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(f"Could not record feedback: {exc}") from exc
    print(f"[green]Performance snapshot recorded:[/green] #{row_id} for {creative_id}")


@radar_app.command("feedback-report")
def radar_feedback_report(
    creative_id: str | None = typer.Option(None, "--creative-id", help="Optional creative ID filter."),
    store_path: Path = typer.Option(Path("data/creative-feedback.sqlite"), "--store"),
    output: Path = typer.Option(Path("output/creative-feedback-report.json"), "--output", "-o"),
) -> None:
    """Summarize stored performance snapshots and descriptive rates."""
    from genforge_marketing.intelligence.creative_feedback import CreativeFeedbackStore
    report = CreativeFeedbackStore(store_path).report(creative_id)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[green]Feedback report saved:[/green] {output}")
    print(f"Creatives: {report['creative_count']} | Snapshots: {report['snapshot_count']}")
    print("[yellow]Descriptive metrics only; use comparable post-age windows and avoid causal claims.[/yellow]")


@radar_app.command("creative-insights")
def radar_creative_insights(
    report_file: Path = typer.Option(..., "--report", exists=True, readable=True, dir_okay=False, help="Creative feedback report JSON."),
    output: Path = typer.Option(Path("output/creative-insights.json"), "--output", "-o"),
) -> None:
    """Generate exploratory creative insights and suggested controlled tests."""
    from genforge_marketing.intelligence.creative_insights import build_creative_insights
    try:
        report = json.loads(report_file.read_text(encoding="utf-8"))
        insights = build_creative_insights(report)
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(f"Could not build creative insights: {exc}") from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(insights, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[green]Creative insights saved:[/green] {output}")
    print(f"Creatives analyzed: {insights['creative_count']} | Suggestions: {len(insights['recommendations'])}")
    print("[yellow]Exploratory comparisons only; results are not causal or statistically validated.[/yellow]")


@radar_app.command("campaign-pack")
def radar_campaign_pack(
    product: str = typer.Option(..., "--product"),
    description: str = typer.Option("", "--description"),
    objective: str = typer.Option("awareness", "--objective"),
    audience: str = typer.Option("people interested in custom 3D printed products", "--audience"),
    platform: str = typer.Option("Instagram Reels", "--platform"),
    duration: int = typer.Option(20, "--duration", min=8, max=90),
    brand_voice: str = typer.Option("creative, helpful, maker-focused", "--brand-voice"),
    breakdown_file: Path | None = typer.Option(None, "--breakdown", exists=True, readable=True, dir_okay=False),
    timeline_file: Path | None = typer.Option(None, "--timeline", exists=True, readable=True, dir_okay=False),
    visual_notes_file: Path | None = typer.Option(None, "--visual-notes", exists=True, readable=True, dir_okay=False),
    brief_output: Path = typer.Option(Path("output/campaign-brief.json"), "--brief-output"),
    handoff_output: Path = typer.Option(Path("output/claude-handoff.md"), "--handoff-output"),
) -> None:
    """Create both the original creative brief and Claude-ready handoff in one offline run."""
    from genforge_marketing.intelligence.campaign_pack import build_campaign_pack, write_campaign_pack
    try:
        breakdown = json.loads(breakdown_file.read_text(encoding="utf-8")) if breakdown_file else None
        timeline = json.loads(timeline_file.read_text(encoding="utf-8")) if timeline_file else None
        visual_notes = json.loads(visual_notes_file.read_text(encoding="utf-8")) if visual_notes_file else None
        pack = build_campaign_pack(product, description, objective, audience, platform, duration, brand_voice, breakdown, timeline, visual_notes)
        brief_path, handoff_path = write_campaign_pack(pack, brief_output, handoff_output)
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(f"Could not assemble campaign pack: {exc}") from exc
    print(f"[green]Campaign brief:[/green] {brief_path}")
    print(f"[green]Claude handoff:[/green] {handoff_path}")
    print("[yellow]Draft package assembled offline; review before production. No external model called.[/yellow]")


@radar_app.command("experiment-report")
def radar_experiment_report(
    experiment_file: Path = typer.Option(..., "--experiment", exists=True, readable=True, dir_okay=False, help="Experiment specification JSON."),
    feedback_file: Path = typer.Option(..., "--feedback", exists=True, readable=True, dir_okay=False, help="Creative feedback report JSON."),
    output: Path = typer.Option(Path("output/experiment-report.json"), "--output", "-o"),
) -> None:
    """Compare declared experiment variants using recorded creative metrics."""
    from genforge_marketing.intelligence.creative_experiments import compare_experiment
    try:
        experiment = json.loads(experiment_file.read_text(encoding="utf-8"))
        feedback = json.loads(feedback_file.read_text(encoding="utf-8"))
        report = compare_experiment(experiment, feedback)
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(f"Could not compare experiment: {exc}") from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[green]Experiment comparison saved:[/green] {output}")
    print(f"Experiment: {report.get('experiment_id') or 'unnamed'} | Variants: {len(report['variants'])}")
    print("[yellow]Descriptive results only; no causal or statistical significance claims.[/yellow]")


@radar_app.command("campaign-init")
def radar_campaign_init(
    name: str = typer.Option(..., "--name"),
    product: str = typer.Option(..., "--product"),
    objective: str = typer.Option("awareness", "--objective"),
    platform: str = typer.Option("Instagram Reels", "--platform"),
    audience: str = typer.Option("", "--audience"),
    root: Path = typer.Option(Path("campaigns"), "--root"),
) -> None:
    """Create a local campaign workspace and starter experiment."""
    from genforge_marketing.intelligence.campaign_workspace import create_campaign_workspace
    result = create_campaign_workspace(root, name, product, objective, platform, audience)
    print(f"[green]Campaign workspace created:[/green] {result['workspace']}")
    print(f"Folders: {', '.join(result['folders'])}")
    print("[yellow]Workspace initialized locally; no external APIs called.[/yellow]")


@radar_app.command("campaign-status")
def radar_campaign_status(
    campaign: Path = typer.Option(..., "--campaign", exists=True, readable=True),
) -> None:
    """Show campaign stages and the next incomplete action."""
    from genforge_marketing.intelligence.campaign_orchestrator import load_campaign, status_report
    try:
        report = status_report(load_campaign(campaign))
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(f"Cannot read campaign: {exc}") from exc
    table = Table(title=f"Campaign: {report.get('campaign_name')}")
    table.add_column("Stage")
    table.add_column("Status")
    for stage in report["stages"]:
        table.add_row(stage["label"], stage["status"])
    print(table)
    print(f"Next stage: {report['next_stage'] or 'all stages complete'}")
    print("[yellow]Review and publishing require human approval.[/yellow]")


@radar_app.command("campaign-stage")
def radar_campaign_stage(
    campaign: Path = typer.Option(..., "--campaign", exists=True, readable=True, dir_okay=False),
    stage: str = typer.Option(..., "--stage"),
    status: str = typer.Option(..., "--status"),
    note: str = typer.Option("", "--note"),
) -> None:
    """Update the status of a campaign stage in its manifest."""
    from genforge_marketing.intelligence.campaign_orchestrator import update_stage
    try:
        update_stage(campaign, stage, status, note)
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    print(f"[green]Updated[/green] {stage} → {status}")


@radar_app.command("campaign-audit")
def radar_campaign_audit(
    campaign: Path = typer.Option(..., "--campaign", exists=True, readable=True),
) -> None:
    """Check existence of campaign deliverables declared in campaign.json."""
    from genforge_marketing.intelligence.campaign_artifact_audit import audit_artifacts
    try:
        report = audit_artifacts(campaign)
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(f"Campaign audit failed: {exc}") from exc
    table = Table(title=f"Campaign artifact audit: {report.get('campaign_name')}")
    table.add_column("Stage")
    table.add_column("Artifact")
    table.add_column("Status")
    for item in report["checks"]:
        table.add_row(item["stage"], item["path"], "[green]Found[/green]" if item["exists"] else "[red]Missing[/red]")
    print(table)
    print(f"Checked: {report['checked_count']} | Found: {report['existing_count']} | Missing: {report['missing_count']}")
    print("[yellow]This audit does not automatically mark stages complete.[/yellow]")


@radar_app.command("campaign-plan")
def radar_campaign_plan(
    campaign: Path = typer.Option(..., "--campaign", exists=True, readable=True),
    output: Path | None = typer.Option(None, "--output", "-o"),
) -> None:
    """Plan the next campaign action from stage progress and artifact checks."""
    from genforge_marketing.intelligence.campaign_execution_plan import campaign_plan
    try:
        plan = campaign_plan(campaign)
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(f"Campaign planning failed: {exc}") from exc
    print(f"[bold cyan]Campaign:[/bold cyan] {plan['campaign_name']}")
    print(f"[bold]Next stage:[/bold] {plan['next_stage'] or 'complete'}")
    print(plan["next_action"])
    if plan["missing_artifacts_for_next_stage"]:
        print("[yellow]Missing deliverables for this stage:[/yellow]")
        for item in plan["missing_artifacts_for_next_stage"]:
            print(f" • {item['path']}")
    if plan["approval_required"]:
        print("[yellow]Human approval is required for this stage.[/yellow]")
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
        print(f"[green]Execution plan saved:[/green] {output}")
    print("[yellow]Planner is advisory only; no files or external actions were executed.[/yellow]")


@radar_app.command("visual-notes")
def radar_visual_notes(
    media_file: Path = typer.Option(..., "--media", exists=True, readable=True, dir_okay=False, help="Media inspection JSON containing sampled frame references."),
    output: Path = typer.Option(Path("output/frame-visual-notes.json"), "--output", "-o"),
) -> None:
    """Create an editable frame-by-frame visual observation template."""
    from genforge_marketing.intelligence.visual_notes import build_visual_notes_template
    try:
        media = json.loads(media_file.read_text(encoding="utf-8"))
        report = build_visual_notes_template(media)
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(f"Could not create frame notes: {exc}") from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[green]Frame notes template created:[/green] {output}")
    print(f"Frames to annotate: {len(report['frames'])}")
    print("[yellow]Fill observations manually; no visual AI analysis has been performed.[/yellow]")


@radar_app.command("storyboard")
def radar_storyboard(
    timeline_file: Path = typer.Option(..., "--timeline", exists=True, readable=True, dir_okay=False, help="Reconstructed timeline JSON."),
    output: Path = typer.Option(Path("output/reel-storyboard.html"), "--output", "-o"),
    frames_dir: Path | None = typer.Option(None, "--frames-dir", help="Directory containing sampled frame images."),
) -> None:
    """Render a standalone HTML storyboard for reviewing Reel structure."""
    from genforge_marketing.intelligence.storyboard import write_storyboard
    try:
        report = json.loads(timeline_file.read_text(encoding="utf-8"))
        destination = write_storyboard(report, output, frames_dir)
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(f"Could not build storyboard: {exc}") from exc
    summary = report.get("evidence_summary", {})
    print(f"[green]Storyboard created:[/green] {destination}")
    print(f"Events: {report.get('event_count', len(report.get('timeline', [])))}")
    print(f"Frames: {summary.get('sampled_frames', 0)} | Scene changes: {summary.get('scene_changes', 0)} | Transcript segments: {summary.get('transcript_segments', 0)}")
    print("[yellow]Open the HTML locally. Frame meaning and heuristic labels still require human review.[/yellow]")


@radar_app.command("transcribe-audio")
def radar_transcribe_audio(
    input_file: Path = typer.Option(..., "--input", exists=True, readable=True, dir_okay=False, help="Audio file, preferably the WAV from inspect-audio."),
    output: Path = typer.Option(Path("output/transcription.json"), "--output", "-o"),
    model_size: str = typer.Option("base", "--model", help="Whisper model size: tiny, base, small, medium, large-v3."),
    device: str = typer.Option("cpu", "--device", help="cpu or cuda (requires compatible local setup)."),
    compute_type: str = typer.Option("int8", "--compute-type", help="faster-whisper compute type."),
    language: str | None = typer.Option(None, "--language", help="Optional language code, e.g. en or hi."),
) -> None:
    """Transcribe audio locally with the optional faster-whisper package."""
    from genforge_marketing.intelligence.transcriber import TranscriptionError, transcribe_audio

    try:
        report = transcribe_audio(input_file, model_size, device, compute_type, language)
    except (TranscriptionError, ValueError, FileNotFoundError) as exc:
        print("[red]Transcription failed:[/red]", exc)
        raise typer.Exit(code=1) from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[green]Transcription saved:[/green] {output}")
    print(f"Language: {report.get('language') or 'unknown'}")
    print(f"Segments: {len(report['segments'])}")
    print("[yellow]Local speech transcription only; verify transcript accuracy before using it.[/yellow]")


@radar_app.command("detect-scenes")
def radar_detect_scenes(
    input_file: Path = typer.Option(..., "--input", exists=True, readable=True, dir_okay=False, help="Local video file."),
    threshold: float = typer.Option(0.30, "--threshold", min=0.0, max=1.0, help="Scene sensitivity threshold (0-1)."),
    output: Path = typer.Option(Path("output/scene-changes.json"), "--output", "-o"),
) -> None:
    """Detect visual scene changes in a local video with FFmpeg."""
    from genforge_marketing.intelligence.media_inspector import MediaInspectionError
    from genforge_marketing.intelligence.scene_detector import detect_scene_changes

    try:
        report = detect_scene_changes(input_file, threshold)
    except (MediaInspectionError, ValueError, FileNotFoundError) as exc:
        print(f"[red]Scene detection failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[green]Scene-change report saved:[/green] {output}")
    print(f"Detected changes: {report['scene_change_count']}")
    print("[yellow]Visual change detection only; scene labels and narrative roles are not inferred.[/yellow]")


@radar_app.command("inspect-media")
def radar_inspect_media(
    input_file: Path = typer.Option(..., "--input", exists=True, readable=True, dir_okay=False, help="Local video file."),
    output: Path = typer.Option(Path("output/media-inspection.json"), "--output", "-o"),
    frames_dir: Path = typer.Option(Path("output/media-frames"), "--frames-dir", help="Directory for sampled JPG frames."),
    interval: float = typer.Option(2.0, "--interval", min=0.1, help="Seconds between sampled frames."),
) -> None:
    """Inspect local video metadata and sample frames; requires FFmpeg and FFprobe."""
    from genforge_marketing.intelligence.media_inspector import MediaInspectionError, inspect_media

    try:
        report = inspect_media(input_file, frames_dir, interval)
    except (MediaInspectionError, ValueError, FileNotFoundError) as exc:
        print(f"[red]Media inspection failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[green]Media inspection saved:[/green] {output}")
    print(f"Duration: {report['metadata']['duration_seconds']:.2f}s")
    print(f"Frames sampled: {report['sampling']['frame_count']}")
    print(f"Frames directory: {frames_dir}")
    print("[yellow]Frames are indexed only; no visual analysis or transcription was performed.[/yellow]")


@radar_app.command("autopsy")
def radar_autopsy(
    input_file: Path = typer.Option(..., "--input", exists=True, readable=True, dir_okay=False, help="JSON containing reference metadata and analyst-observed beats."),
    output: Path = typer.Option(Path("output/reel-autopsy.json"), "--output", "-o"),
) -> None:
    """Reconstruct a Reel/post creative blueprint from supplied observations."""
    from genforge_marketing.intelligence.reel_autopsy import ReferenceInput, build_autopsy

    try:
        reference = ReferenceInput.model_validate_json(input_file.read_text(encoding="utf-8"))
        report = build_autopsy(reference)
    except (ValueError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[green]Autopsy report saved:[/green] {output}")
    print(f"Reference: {reference.title}")
    print(f"Observed beats: {len(report['timeline'])}")
    print(f"Hook: {reference.hook_observation or 'not supplied'}")
    print(f"Payoff: {reference.payoff_observation or 'not supplied'}")
    print("[yellow]Evidence-aware reconstruction only; no media was automatically fetched or inspected.[/yellow]")


@radar_app.command("compare")
def radar_compare(
    signal_id: str = typer.Argument(..., help="Stable signal ID from a prior import."),
    store: Path = typer.Option(Path("data/trend-history.sqlite"), "--store"),
) -> None:
    """Compare stored snapshots and report observed metric velocity."""
    from genforge_marketing.intelligence.trend_history import TrendHistoryStore
    result = TrendHistoryStore(store).compare(signal_id)
    print(json.dumps(result, indent=2, ensure_ascii=False))


@radar_app.command("import-screening")
def radar_import_screening(
    input_file: Path = typer.Option(..., "--input", exists=True, readable=True, dir_okay=False),
    output: Path = typer.Option(Path("output/screening-radar-report.json"), "--output", "-o"),
    history_store: Path = typer.Option(Path("data/trend-history.sqlite"), "--history-store", help="SQLite file for automatic snapshot history."),
) -> None:
    """Import a Screening Agent JSON export, rank signals, and record history snapshots."""
    from genforge_marketing.integrations.screening_cli import load_screening_export, ScreeningCLIError

    try:
        batch = load_screening_export(input_file)
        signals = []
        for item in batch.items:
            raw = item.raw if isinstance(item.raw, dict) else {}
            published_at = raw.get("published_at")
            shares = raw.get("shares")
            creator = raw.get("creator")
            search_term = raw.get("search_term")
            available = [
                item.source,
                item.source_url,
                item.observed_at,
                item.views,
                item.likes,
                item.comments,
                shares,
                creator,
                published_at,
            ]
            completeness = sum(value not in (None, "") for value in available) / len(available)
            signals.append(
                TrendSignal(
                    title=item.topic,
                    platform=item.source,
                    url=item.source_url,
                    creator=creator,
                    published_at=published_at,
                    collected_at=item.observed_at,
                    views=item.views,
                    likes=item.likes,
                    comments=item.comments,
                    shares=shares,
                    category=str(search_term or "screening-import"),
                    notes=item.summary,
                    data_completeness=round(completeness, 4),
                )
            )
        from genforge_marketing.intelligence.trend_history import TrendHistoryStore
        history = TrendHistoryStore(history_store)
        history_ids = [history.record(signal) for signal in signals]
        report = build_report(signals)
        report["history"] = {"store": str(history_store), "recorded_snapshots": len(history_ids), "signal_ids": history_ids}
        report["source_agent"] = batch.source_agent
        report["source_file"] = str(input_file)
    except (ScreeningCLIError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    table = Table(title=f"Screening import — {len(signals)} signals")
    table.add_column("Trend")
    table.add_column("Score", justify="right")
    table.add_column("Confidence", justify="right")
    for row in report["ranked_signals"][:20]:
        table.add_row(row["signal"]["title"], f"{row['score']:.3f}", f"{row['confidence']:.2f}")
    print(table)
    print(f"[green]Radar report saved:[/green] {output}")
    print("[yellow]Imported metrics are source-provided snapshots; rankings are heuristic.[/yellow]")


@radar_app.command("scan")
def radar_scan(
    fixture: Path = typer.Option(..., "--fixture", exists=True, readable=True, dir_okay=False, help="JSON array of TrendSignal records."),
    category: str = typer.Option("all", "--category"),
    output: Path = typer.Option(Path("output/radar-report.json"), "--output", "-o"),
) -> None:
    """Score and rank signals from a local fixture file."""
    signals = load_fixture(fixture)
    if category != "all":
        signals = [signal for signal in signals if signal.category == category]
    report = build_report(signals)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    table = Table(title=f"Trend Radar — {len(signals)} signals")
    table.add_column("Signal")
    table.add_column("Score", justify="right")
    table.add_column("Confidence", justify="right")
    for row in report["ranked_signals"][:20]:
        table.add_row(row["signal"]["title"], f"{row['score']:.3f}", f"{row['confidence']:.2f}")
    print(table)
    print(f"[green]Report saved:[/green] {output}")
    print("[yellow]Heuristic ranking only; fixture inputs, no live platform claims.[/yellow]")


@radar_app.command("analyze-reference")
def radar_analyze_reference(
    signal_file: Path = typer.Option(..., "--signal", exists=True, readable=True, dir_okay=False),
    dna_file: Path = typer.Option(..., "--dna", exists=True, readable=True, dir_okay=False, help="Analysis notes JSON describing accessible reference media."),
    store: Path = typer.Option(Path("data/radar.sqlite"), "--store"),
) -> None:
    """Save a reference and its supplied Creative DNA notes."""
    signal = TrendSignal.model_validate_json(signal_file.read_text(encoding="utf-8"))
    dna = CreativeDNA.model_validate_json(dna_file.read_text(encoding="utf-8"))
    reference = Reference(signal=signal, dna=dna)
    ref_id = ReferenceStore(store).add(reference)
    print(f"[green]Saved creative reference:[/green] {ref_id}")
    print(json.dumps(score_signal(signal), indent=2))
    print("[yellow]Analysis notes are user-supplied; this command does not watch or analyze video automatically.[/yellow]")


@radar_app.command("references")
def radar_references(
    store: Path = typer.Option(Path("data/radar.sqlite"), "--store"),
    category: str | None = typer.Option(None, "--category"),
    show: str | None = typer.Option(None, "--show", help="Reference ID to display."),
) -> None:
    """List saved references or show one by ID."""
    db = ReferenceStore(store)
    if show:
        item = db.get(show)
        if item is None:
            raise typer.Exit(code=2)
        print(json.dumps(item, indent=2, ensure_ascii=False))
        return
    items = db.list(category)
    table = Table(title=f"Creative references ({len(items)})")
    table.add_column("ID")
    table.add_column("Category")
    table.add_column("Score", justify="right")
    table.add_column("Title")
    for item in items:
        table.add_row(item["id"], item["category"], f"{item['score']:.3f}", item["reference"]["signal"]["title"])
    print(table)


@radar_app.command("report")
def radar_report(
    fixture: Path = typer.Option(..., "--fixture", exists=True, readable=True, dir_okay=False),
    output: Path = typer.Option(Path("output/radar-report.md"), "--output", "-o"),
) -> None:
    """Export a Markdown summary report from local fixture signals."""
    report = build_report(load_fixture(fixture))
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# GenForge Trend Radar Report", "", f"Generated: {report['generated_at']}", f"Signals: {report['count']}", "", "## Ranked signals", ""]
    for row in report["ranked_signals"]:
        sig = row["signal"]
        lines.extend([f"### {sig['title']}", f"- Platform: {sig['platform']}", f"- Category: {sig['category']}", f"- Score: {row['score']:.3f}", f"- Confidence: {row['confidence']:.2f}", f"- Notes: {sig.get('notes') or 'No notes supplied'}", f"- Source: {sig.get('url') or 'not provided'}", ""])
    lines.extend(["## Limitations", *[f"- {item}" for item in report["limitations"]]])
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[green]Markdown report saved:[/green] {output}")

@radar_app.command("creative-patterns")
def radar_creative_patterns(
    store: Path = typer.Option(Path("data/radar.sqlite"), "--store"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Optional JSON output file."),
) -> None:
    """Summarize recurring Creative DNA patterns across saved references."""
    from genforge_marketing.intelligence.radar import summarize_creative_patterns

    summary = summarize_creative_patterns(ReferenceStore(store).list())
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[green]Creative pattern summary saved:[/green] {output}")

@radar_app.command("rank-products")
def radar_rank_products(
    input_file: Path = typer.Option(..., "--input", exists=True, readable=True, dir_okay=False),
    output: Path = typer.Option(Path("output/product-radar.json"), "--output", "-o"),
) -> None:
    """Rank product candidates using printability, demand, margin and competition inputs."""
    from genforge_marketing.intelligence.product_radar import ProductCandidate, rank_products

    try:
        payload = json.loads(input_file.read_text(encoding="utf-8"))
        candidates = [ProductCandidate.model_validate(item) for item in payload]
        report = rank_products(candidates)
    except (ValueError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    table = Table(title=f"Product Radar — {report['count']} candidates")
    table.add_column("Product")
    table.add_column("Score", justify="right")
    table.add_column("Material cost", justify="right")
    table.add_column("Margin", justify="right")
    for row in report["ranked_products"][:20]:
        cost = row["material_cost_estimate"]
        margin = row["gross_margin_estimate"]
        table.add_row(row["candidate"]["name"], f"{row['score']:.3f}",
                      f"{cost:.2f}" if cost is not None else "n/a",
                      f"{margin:.1%}" if margin is not None else "n/a")
    print(table)
    print(f"[green]Product Radar saved:[/green] {output}")
    print("[yellow]Estimates are screening-level; verify costs and demand before production.[/yellow]")


if __name__ == "__main__":
    app()
