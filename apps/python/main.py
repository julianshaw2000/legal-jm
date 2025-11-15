"""CLI entrypoint for legal document ingestion and AI worker."""

from __future__ import annotations

import logging
import sys

import typer
from dotenv import load_dotenv
from rich.console import Console

from config import Config
from db import DatabaseConnection
from embeddings.service import EmbeddingService
from ingest.service import IngestionService
from ingest.sources.acts import ActsScraper
from ingest.sources.cases import CasesScraper
from ingest.sources.regulations import RegulationsScraper
from logging_conf import setup_logging

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()
logger = logging.getLogger(__name__)


def get_config() -> Config:
    """Load and validate configuration."""
    try:
        return Config.from_env()
    except ValueError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        raise typer.Exit(code=2)


@app.command("healthcheck")
def healthcheck() -> None:
    """Verify database connectivity and source URLs."""
    load_dotenv()
    config = get_config()
    setup_logging(config.log_level)

    console.print("[cyan]Running health check...[/cyan]")

    # Check database
    db = DatabaseConnection(config)
    if db.verify_connection():
        console.print("[green]✓ Database connection OK[/green]")
    else:
        console.print("[red]✗ Database connection failed[/red]")
        raise typer.Exit(code=1)

    # Check source URLs
    if config.scrape_base_url_acts:
        console.print(f"[green]✓ Acts source URL configured[/green]")
    else:
        console.print("[yellow]⚠ Acts source URL not configured[/yellow]")

    if config.scrape_base_url_regulations:
        console.print(f"[green]✓ Regulations source URL configured[/green]")
    else:
        console.print("[yellow]⚠ Regulations source URL not configured[/yellow]")

    if config.scrape_base_url_cases:
        console.print(f"[green]✓ Cases source URL configured[/green]")
    else:
        console.print("[yellow]⚠ Cases source URL not configured[/yellow]")

    # Check OpenAI API key
    if config.openai_api_key:
        console.print("[green]✓ OpenAI API key configured[/green]")
    else:
        console.print("[yellow]⚠ OpenAI API key not configured (embeddings will be skipped)[/yellow]")

    console.print("[green]Health check completed[/green]")


@app.command("ingest-acts")
def ingest_acts() -> None:
    """Scrape and ingest Acts and Statutes."""
    load_dotenv()
    config = get_config()
    setup_logging(config.log_level)

    logger.info("Starting Acts ingestion")
    db = DatabaseConnection(config)

    try:
        with db.get_connection() as conn:
            ingestion_service = IngestionService(config, conn)
            scraper = ActsScraper(config)

            def scrape_func():
                result = scraper.scrape()
                # TODO: Integrate scraper results with ingestion_service
                return result

            result = ingestion_service.run_ingestion_job("Acts", scrape_func)

            if result.success:
                console.print(f"[green]Acts ingestion completed:[/green] {result.message}")
                console.print(f"  Documents found: {result.documents_found}")
                console.print(f"  Documents inserted: {result.documents_inserted}")
                console.print(f"  Documents updated: {result.documents_updated}")
            else:
                console.print(f"[red]Acts ingestion failed:[/red] {result.message}")
                if result.errors:
                    for error in result.errors:
                        console.print(f"  [red]Error:[/red] {error}")
                raise typer.Exit(code=1)
    finally:
        db.close()


@app.command("ingest-regulations")
def ingest_regulations() -> None:
    """Scrape and ingest Regulations."""
    load_dotenv()
    config = get_config()
    setup_logging(config.log_level)

    logger.info("Starting Regulations ingestion")
    db = DatabaseConnection(config)

    try:
        with db.get_connection() as conn:
            ingestion_service = IngestionService(config, conn)
            scraper = RegulationsScraper(config)

            def scrape_func():
                result = scraper.scrape()
                # TODO: Integrate scraper results with ingestion_service
                return result

            result = ingestion_service.run_ingestion_job("Regulations", scrape_func)

            if result.success:
                console.print(f"[green]Regulations ingestion completed:[/green] {result.message}")
                console.print(f"  Documents found: {result.documents_found}")
                console.print(f"  Documents inserted: {result.documents_inserted}")
                console.print(f"  Documents updated: {result.documents_updated}")
            else:
                console.print(f"[red]Regulations ingestion failed:[/red] {result.message}")
                if result.errors:
                    for error in result.errors:
                        console.print(f"  [red]Error:[/red] {error}")
                raise typer.Exit(code=1)
    finally:
        db.close()


@app.command("ingest-cases")
def ingest_cases() -> None:
    """Scrape and ingest Case Law."""
    load_dotenv()
    config = get_config()
    setup_logging(config.log_level)

    logger.info("Starting Cases ingestion")
    db = DatabaseConnection(config)

    try:
        with db.get_connection() as conn:
            ingestion_service = IngestionService(config, conn)
            scraper = CasesScraper(config)

            def scrape_func():
                result = scraper.scrape()
                # TODO: Integrate scraper results with ingestion_service
                return result

            result = ingestion_service.run_ingestion_job("Cases", scrape_func)

            if result.success:
                console.print(f"[green]Cases ingestion completed:[/green] {result.message}")
                console.print(f"  Documents found: {result.documents_found}")
                console.print(f"  Documents inserted: {result.documents_inserted}")
                console.print(f"  Documents updated: {result.documents_updated}")
            else:
                console.print(f"[red]Cases ingestion failed:[/red] {result.message}")
                if result.errors:
                    for error in result.errors:
                        console.print(f"  [red]Error:[/red] {error}")
                raise typer.Exit(code=1)
    finally:
        db.close()


@app.command("ingest-all")
def ingest_all() -> None:
    """Scrape and ingest all legal sources (Acts, Regulations, Cases)."""
    load_dotenv()
    config = get_config()
    setup_logging(config.log_level)

    logger.info("Starting full ingestion")
    console.print("[cyan]Running full ingestion of all sources...[/cyan]")

    db = DatabaseConnection(config)
    has_error = False

    try:
        with db.get_connection() as conn:
            ingestion_service = IngestionService(config, conn)

            # Ingest Acts
            try:
                scraper = ActsScraper(config)
                result = ingestion_service.run_ingestion_job("Acts", scraper.scrape)
                if result.success:
                    console.print(f"[green]Acts:[/green] {result.message}")
                else:
                    console.print(f"[red]Acts failed:[/red] {result.message}")
                    has_error = True
            except Exception as e:
                logger.exception("Acts ingestion error")
                console.print(f"[red]Acts ingestion error:[/red] {e}")
                has_error = True

            # Ingest Regulations
            try:
                scraper = RegulationsScraper(config)
                result = ingestion_service.run_ingestion_job("Regulations", scraper.scrape)
                if result.success:
                    console.print(f"[green]Regulations:[/green] {result.message}")
                else:
                    console.print(f"[red]Regulations failed:[/red] {result.message}")
                    has_error = True
            except Exception as e:
                logger.exception("Regulations ingestion error")
                console.print(f"[red]Regulations ingestion error:[/red] {e}")
                has_error = True

            # Ingest Cases
            try:
                scraper = CasesScraper(config)
                result = ingestion_service.run_ingestion_job("Cases", scraper.scrape)
                if result.success:
                    console.print(f"[green]Cases:[/green] {result.message}")
                else:
                    console.print(f"[red]Cases failed:[/red] {result.message}")
                    has_error = True
            except Exception as e:
                logger.exception("Cases ingestion error")
                console.print(f"[red]Cases ingestion error:[/red] {e}")
                has_error = True

    finally:
        db.close()

    if has_error:
        console.print("[red]Some ingestion jobs failed - see errors above[/red]")
        raise typer.Exit(code=1)
    else:
        console.print("[green]All ingestion jobs completed[/green]")


@app.command("update-embeddings")
def update_embeddings(
    document_id: str | None = typer.Option(None, "--document-id", help="Process specific document only"),
    batch_size: int = typer.Option(100, "--batch-size", help="Batch size for processing"),
) -> None:
    """Generate or update embeddings for document chunks."""
    load_dotenv()
    config = get_config()
    setup_logging(config.log_level)

    if not config.openai_api_key:
        console.print("[red]OpenAI API key not configured - cannot generate embeddings[/red]")
        raise typer.Exit(code=2)

    logger.info("Starting embedding update")
    db = DatabaseConnection(config)

    try:
        with db.get_connection() as conn:
            embedding_service = EmbeddingService(config, conn)

            if document_id:
                console.print(f"[cyan]Processing embeddings for document:[/cyan] {document_id}")
                processed = embedding_service.process_document_chunks(document_id)
                console.print(f"[green]Processed {processed} chunks[/green]")
            else:
                console.print("[cyan]Processing all chunks without embeddings...[/cyan]")
                stats = embedding_service.update_all_embeddings(batch_size)
                console.print(f"[green]Embedding update completed:[/green]")
                console.print(f"  Processed: {stats['processed']}")
                console.print(f"  Failed: {stats['failed']}")
                console.print(f"  Skipped: {stats['skipped']}")
    finally:
        db.close()


@app.command("verify-db")
def verify_db() -> None:
    """Verify database connectivity (alias for healthcheck)."""
    healthcheck()


def main() -> None:
    """Main entrypoint."""
    load_dotenv()
    app()


if __name__ == "__main__":
    main()
