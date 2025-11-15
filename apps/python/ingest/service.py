"""Main ingestion service that orchestrates scraping and persistence."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.engine import Connection

from ..config import Config
from ..db.repositories import (
    DocumentRepository,
    IngestionJobRepository,
    SectionRepository,
    SourceRepository,
)
from ..models import DocumentType, ParsedDocument, ScrapeResult
from .parser import DocumentParser

logger = logging.getLogger(__name__)


class IngestionService:
    """Orchestrates document ingestion workflow."""

    def __init__(self, config: Config, conn: Connection) -> None:
        """Initialize ingestion service."""
        self.config = config
        self.conn = conn
        self.parser = DocumentParser()
        self.source_repo = SourceRepository(conn)
        self.document_repo = DocumentRepository(conn)
        self.section_repo = SectionRepository(conn)
        self.job_repo = IngestionJobRepository(conn)

    def ingest_document(
        self,
        parsed: ParsedDocument,
        source_name: str,
        source_url: str | None = None,
    ) -> tuple[str, bool]:
        """
        Ingest a parsed document into the database.

        Returns (document_id, is_new) tuple.
        """
        # Find or create source
        source_id = self.source_repo.find_or_create(source_name, source_url)

        # Check if document already exists
        existing = self.document_repo.find_by_title_and_type(parsed.title, parsed.document_type)

        if existing:
            # Check if content has changed
            existing_hash = self.document_repo.compute_content_hash(parsed.raw_text)
            if parsed.content_hash and existing_hash == parsed.content_hash:
                logger.debug(f"Document '{parsed.title}' unchanged, skipping")
                return existing["id"], False

            # Update existing document
            self.document_repo.update(existing["id"], parsed)
            document_id = existing["id"]
            is_new = False

            # Delete old sections and recreate
            self.section_repo.delete_by_document(document_id)
        else:
            # Create new document
            document_id = self.document_repo.create(parsed, source_id)
            is_new = True

        # Insert sections
        if parsed.sections:
            self.section_repo.create_batch(document_id, parsed.sections)

        return document_id, is_new

    def run_ingestion_job(
        self,
        source: str,
        scrape_func: Any,
    ) -> ScrapeResult:
        """Run an ingestion job with tracking."""
        job_id = self.job_repo.create(source, "RUNNING")

        try:
            result = scrape_func()
            status = "COMPLETED" if result.success else "FAILED"
            error_msg = "; ".join(result.errors) if result.errors else None
            self.job_repo.update_status(job_id, status, error_msg)
            return result
        except Exception as e:
            logger.exception(f"Ingestion job failed: {e}")
            self.job_repo.update_status(job_id, "FAILED", str(e))
            return ScrapeResult(
                success=False,
                errors=[str(e)],
                message=f"Job failed: {e}",
            )

