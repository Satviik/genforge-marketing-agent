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
from genforge_marketing.workbook.exporter import export_monthly_plan

app = typer.Typer(help="GenForge marketing planning and operations.")


@app.command()
def version() -> None:
    """Show the installed package version."""
    print(f"GenForge Marketing Agent [bold cyan]v{__version__}[/bold cyan]")


@app.command("init-profile")
def init_profile(
    output: Path = typer.Option(Path("genforge-business.json"), "--output", "-o"),
) -> None:
    """Create an editable GenForge business profile template."""
    if output.exists():
        raise typer.BadParameter(f"{output} already exists; choose another path to avoid overwriting.")
    output.parent.mkdir(parents=True, exist_ok=True)
    profile = BusinessProfile()
    output.write_text(profile.model_dump_json(indent=2) + "\\n", encoding="utf-8")
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
    output: Path = typer.Option(Path("output/content-plan.xlsx"), "--output", "-o"),
) -> None:
    """Generate a monthly draft calendar and a two-sheet Excel workbook."""
    try:
        profile = BusinessProfile.model_validate_json(profile_file.read_text(encoding="utf-8"))
        plan = generate_monthly_plan(
            profile=profile,
            year=year,
            month=month,
            post_count=posts,
            reel_count=reels,
            post_time=time.fromisoformat(post_time),
            reel_time=time.fromisoformat(reel_time),
        )
    except (ValueError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    workbook_path = export_monthly_plan(plan, output)
    json_path = output.with_suffix(".json")
    json_path.write_text(plan.model_dump_json(indent=2) + "\\n", encoding="utf-8")

    table = Table(title=f"GenForge content plan — {year}-{month:02d}")
    table.add_column("Format")
    table.add_column("Items", justify="right")
    table.add_row("Posts", str(len(plan.posts)))
    table.add_row("Reels", str(len(plan.reels)))
    print(table)
    print(f"[green]Excel workbook:[/green] {workbook_path}")
    print(f"[green]Editable plan data:[/green] {json_path}")
    print("[yellow]All items are drafts. Nothing has been published.[/yellow]")


if __name__ == "__main__":
    app()
