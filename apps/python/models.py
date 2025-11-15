"""Pydantic models for internal data structures."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class DocumentType(str, Enum):
    """Document type enumeration matching Prisma schema."""

    ACT = "ACT"
    REGULATION = "REGULATION"
    CASE = "CASE"
    OTHER = "OTHER"


@dataclass
class ParsedDocument:
    """Parsed document structure before DB insertion."""

    title: str
    document_type: DocumentType
    source_url: str
    citation: str | None = None
    jurisdiction: str = "JM"
    date_enacted: datetime | None = None
    date_commenced: datetime | None = None
    date_last_amended: datetime | None = None
    published_at: datetime | None = None
    raw_text: str = ""
    sections: list[ParsedSection] | None = None
    content_hash: str | None = None  # Computed hash for change detection


@dataclass
class ParsedSection:
    """Parsed section structure."""

    index: int
    heading: str | None = None
    text: str = ""


@dataclass
class ScrapeResult:
    """Result of a scraping operation."""

    success: bool
    documents_found: int = 0
    documents_inserted: int = 0
    documents_updated: int = 0
    errors: list[str] | None = None
    message: str = ""

    def __post_init__(self) -> None:
        """Initialize errors list if None."""
        if self.errors is None:
            self.errors = []


class ChunkMetadata(BaseModel):
    """Metadata for a text chunk."""

    document_id: str
    section_id: str | None = None
    index: int
    text: str
    area_of_law: str | None = None
    tags: list[str] | None = None

