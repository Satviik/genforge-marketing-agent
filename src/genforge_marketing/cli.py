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

if __name__ == "__main__":
    app()
