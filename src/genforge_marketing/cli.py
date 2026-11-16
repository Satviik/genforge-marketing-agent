"""Command-line interface for GenForge Marketing Agent."""

from pathlib import Path

import typer
from rich import print
from rich.table import Table

from genforge_marketing.content.briefs import build_brief
from genforge_marketing.integrations.screening_cli import ScreeningCLIError, load_screening_export
from genforge_marketing.intelligence.scoring import score_opportunity

app = typer.Typer(help="GenForge marketing operations and content intelligence.")


@app.command()
def version() -> None:
    """Show the installed package version."""
    from genforge_marketing import __version__

    print(f"GenForge Marketing Agent [bold cyan]v{__version__}[/bold cyan]")


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
