from __future__ import annotations

import os
import sys
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()


def get_engine() -> Engine:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        console.print("[red]DATABASE_URL is not set[/red]")
        raise typer.Exit(code=2)
    return create_engine(db_url, pool_pre_ping=True)


@app.command("verify-db")
def verify_db() -> None:
    """Verify database connectivity."""
    load_dotenv()
    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        console.print("[green]Database connection OK[/green]")
    except SQLAlchemyError as exc:
        console.print(f"[red]Database connection failed:[/red] {exc}")
        raise typer.Exit(code=1)


@app.command("scrape")
def scrape(which: str = typer.Argument(..., help="acts|cases|regulations|all")) -> None:
    """Scrape legal sources and populate the database (skeleton)."""
    load_dotenv()
    console.print(f"[cyan]Scrape command:[/cyan] {which}")
    # TODO: Implement scrapers. For now, just signal success.
    console.print("[yellow]Scraper skeleton - not yet implemented[/yellow]")


@app.command("rebuild-index")
def rebuild_index() -> None:
    """Rebuild embeddings index (skeleton)."""
    load_dotenv()
    console.print("[cyan]Rebuilding index (skeleton)[/cyan]")


def main() -> None:
    load_dotenv()
    app()


if __name__ == "__main__":
    main()
