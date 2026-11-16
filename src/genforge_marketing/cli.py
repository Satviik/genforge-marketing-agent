"""Command-line interface for GenForge Marketing Agent."""

from pathlib import Path

import typer
from rich import print
from rich.table import Table

from genforge_marketing.config import get_settings
from genforge_marketing.content.briefs import build_brief
from genforge_marketing.integrations.screening_cli import (
    ScreeningCLIError,
    load_screening_export,
    run_screening_export,
)
from genforge_marketing.intelligence.scoring import score_opportunity

app = typer.Typer(help="GenForge marketing operations and content intelligence.")


@app.command()
def version() -> None:
    """Show the installed package version."""
    from genforge_marketing import __version__

    print(f"GenForge Marketing Agent [bold cyan]v{__version__}[/bold cyan]")


@app.command("sync-trends")
def sync_trends(
    limit: int = typer.Option(200, "--limit", "-n", min=1, max=5000),
) -> None:
    """Run the screening CLI's JSON export and import its trend records."""
    settings = get_settings()
    try:
        batch = run_screening_export(
            command=settings.screening_command,
            timeout_seconds=settings.screening_timeout_seconds,
            limit=limit,
            working_directory=settings.screening_workdir,
        )
    except ScreeningCLIError as exc:
        print(f"[red]Could not sync screening trends:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title=f"Screening sync complete ({len(batch.items)} opportunities)")
    table.add_column("Topic")
    table.add_column("Source")
    table.add_column("Score", justify="right")
    for item in sorted(batch.items, key=score_opportunity, reverse=True):
        table.add_row(item.topic, item.source, f"{score_opportunity(item):.4f}")
    print(table)


@app.command("import-trends")
def import_trends(
    file: Path = typer.Argument(..., exists=True, readable=True, dir_okay=False),
) -> None:
    """Import a JSON export from gen-forge-screening-agent."""
    try:
        batch = load_screening_export(file)
    except ScreeningCLIError as exc:
        raise typer.BadParameter(str(exc)) from exc

    table = Table(title=f"Imported opportunities ({len(batch.items)})")
    table.add_column("Topic")
    table.add_column("Source")
    table.add_column("Score", justify="right")
    for item in sorted(batch.items, key=score_opportunity, reverse=True):
        table.add_row(item.topic, item.source, f"{score_opportunity(item):.4f}")
    print(table)


@app.command()
def brief(
    file: Path = typer.Argument(..., exists=True, readable=True, dir_okay=False),
) -> None:
    """Create a deterministic content brief from the first item in an export."""
    try:
        batch = load_screening_export(file)
    except ScreeningCLIError as exc:
        raise typer.BadParameter(str(exc)) from exc

    if not batch.items:
        raise typer.BadParameter("The screening export contains no opportunities.")

    result = build_brief(max(batch.items, key=score_opportunity))
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
