"""Database repositories for legal data models."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection

from ..models import DocumentType, ParsedDocument, ParsedSection


class SourceRepository:
    """Repository for Source model."""

    def __init__(self, conn: Connection) -> None:
        """Initialize repository with database connection."""
        self.conn = conn

    def find_or_create(self, name: str, url: str | None = None) -> str:
        """Find or create a source and return its ID."""
        # Check if source exists
        result = self.conn.execute(
            text("SELECT id FROM \"Source\" WHERE name = :name"),
            {"name": name},
        ).fetchone()

        if result:
            return result[0]

        # Create new source
        result = self.conn.execute(
            text(
                """
                INSERT INTO "Source" (id, name, url, "createdAt")
                VALUES (gen_random_uuid()::text, :name, :url, NOW())
                RETURNING id
                """
            ),
            {"name": name, "url": url},
        )
        return result.fetchone()[0]


class DocumentRepository:
    """Repository for Document model."""

    def __init__(self, conn: Connection) -> None:
        """Initialize repository with database connection."""
        self.conn = conn

    def compute_content_hash(self, text_content: str) -> str:
        """Compute SHA256 hash of normalized text content."""
        normalized = text_content.strip().lower().replace("\r\n", "\n").replace("\r", "\n")
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def find_by_source_url(self, source_url: str) -> dict[str, Any] | None:
        """Find document by source URL (assuming we store it in a metadata field or similar)."""
        # Note: Prisma schema doesn't have source_url field directly on Document
        # We'll need to check if there's a way to store this, or use Source.url
        # For now, we'll check by title and type matching
        return None

    def find_by_title_and_type(self, title: str, doc_type: DocumentType) -> dict[str, Any] | None:
        """Find document by title and type."""
        result = self.conn.execute(
            text(
                """
                SELECT id, title, type, "publishedAt", "createdAt", "updatedAt"
                FROM "Document"
                WHERE title = :title AND type = :type
                ORDER BY "createdAt" DESC
                LIMIT 1
                """
            ),
            {"title": title, "type": doc_type.value},
        ).fetchone()

        if not result:
            return None

        return {
            "id": result[0],
            "title": result[1],
            "type": result[2],
            "published_at": result[3],
            "created_at": result[4],
            "updated_at": result[5],
        }

    def create(
        self,
        parsed: ParsedDocument,
        source_id: str | None = None,
    ) -> str:
        """Create a new document and return its ID."""
        result = self.conn.execute(
            text(
                """
                INSERT INTO "Document" (
                    id, "sourceId", title, type, "publishedAt", "createdAt", "updatedAt"
                )
                VALUES (
                    gen_random_uuid()::text,
                    :source_id,
                    :title,
                    :type,
                    :published_at,
                    NOW(),
                    NOW()
                )
                RETURNING id
                """
            ),
            {
                "source_id": source_id,
                "title": parsed.title,
                "type": parsed.document_type.value,
                "published_at": parsed.published_at or parsed.date_enacted,
            },
        )
        return result.fetchone()[0]

    def update(self, document_id: str, parsed: ParsedDocument) -> None:
        """Update an existing document."""
        self.conn.execute(
            text(
                """
                UPDATE "Document"
                SET title = :title,
                    "publishedAt" = :published_at,
                    "updatedAt" = NOW()
                WHERE id = :id
                """
            ),
            {
                "id": document_id,
                "title": parsed.title,
                "published_at": parsed.published_at or parsed.date_enacted,
            },
        )


class SectionRepository:
    """Repository for Section model."""

    def __init__(self, conn: Connection) -> None:
        """Initialize repository with database connection."""
        self.conn = conn

    def delete_by_document(self, document_id: str) -> None:
        """Delete all sections for a document (for re-import)."""
        self.conn.execute(
            text('DELETE FROM "Section" WHERE "documentId" = :document_id'),
            {"document_id": document_id},
        )

    def create(self, document_id: str, section: ParsedSection) -> str:
        """Create a section and return its ID."""
        result = self.conn.execute(
            text(
                """
                INSERT INTO "Section" (
                    id, "documentId", index, heading, text, "createdAt"
                )
                VALUES (
                    gen_random_uuid()::text,
                    :document_id,
                    :index,
                    :heading,
                    :text,
                    NOW()
                )
                RETURNING id
                """
            ),
            {
                "document_id": document_id,
                "index": section.index,
                "heading": section.heading,
                "text": section.text,
            },
        )
        return result.fetchone()[0]

    def create_batch(self, document_id: str, sections: list[ParsedSection]) -> list[str]:
        """Create multiple sections in a batch."""
        ids = []
        for section in sections:
            ids.append(self.create(document_id, section))
        return ids


class IngestionJobRepository:
    """Repository for IngestionJob model."""

    def __init__(self, conn: Connection) -> None:
        """Initialize repository with database connection."""
        self.conn = conn

    def create(self, source: str, status: str = "RUNNING") -> str:
        """Create a new ingestion job and return its ID."""
        result = self.conn.execute(
            text(
                """
                INSERT INTO "IngestionJob" (id, source, status, "startedAt")
                VALUES (gen_random_uuid()::text, :source, :status, NOW())
                RETURNING id
                """
            ),
            {"source": source, "status": status},
        )
        return result.fetchone()[0]

    def update_status(self, job_id: str, status: str, error: str | None = None) -> None:
        """Update job status."""
        self.conn.execute(
            text(
                """
                UPDATE "IngestionJob"
                SET status = :status,
                    "finishedAt" = CASE WHEN :status IN ('COMPLETED', 'FAILED') THEN NOW() ELSE NULL END,
                    error = :error
                WHERE id = :id
                """
            ),
            {"id": job_id, "status": status, "error": error},
        )

