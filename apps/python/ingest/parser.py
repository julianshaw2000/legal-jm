"""Document parsing and extraction utilities."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from ..models import DocumentType, ParsedDocument, ParsedSection
from .normalizer import DocumentNormalizer


class DocumentParser:
    """Parses HTML/text content into structured documents."""

    def __init__(self) -> None:
        """Initialize parser with normalizer."""
        self.normalizer = DocumentNormalizer()

    def parse_html(self, html_content: str, source_url: str, doc_type: DocumentType) -> ParsedDocument:
        """Parse HTML content into a ParsedDocument."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract title
        title = self._extract_title(soup)

        # Extract citation if available
        citation = self._extract_citation(soup, html_content)

        # Extract dates
        dates = self._extract_dates(soup, html_content)

        # Clean and extract text
        raw_text = self.normalizer.clean_html(html_content)

        # Extract sections
        sections_data = self.normalizer.extract_sections(raw_text)
        sections = [
            ParsedSection(index=idx, heading=heading, text=text)
            for idx, heading, text in sections_data
        ]

        # Compute content hash
        content_hash = self._compute_hash(raw_text)

        return ParsedDocument(
            title=title,
            document_type=doc_type,
            source_url=source_url,
            citation=citation,
            date_enacted=dates.get("enacted"),
            date_commenced=dates.get("commenced"),
            date_last_amended=dates.get("amended"),
            published_at=dates.get("published"),
            raw_text=raw_text,
            sections=sections if sections else None,
            content_hash=content_hash,
        )

    def parse_text(self, text_content: str, source_url: str, doc_type: DocumentType) -> ParsedDocument:
        """Parse plain text content into a ParsedDocument."""
        # Normalize text
        normalized_text = self.normalizer.normalize_text(text_content)

        # Try to extract title (first line or before first section)
        title = self._extract_title_from_text(normalized_text)

        # Extract citation
        citation = self._extract_citation_from_text(normalized_text)

        # Extract dates
        dates = self._extract_dates_from_text(normalized_text)

        # Extract sections
        sections_data = self.normalizer.extract_sections(normalized_text)
        sections = [
            ParsedSection(index=idx, heading=heading, text=text)
            for idx, heading, text in sections_data
        ]

        # Compute content hash
        content_hash = self._compute_hash(normalized_text)

        return ParsedDocument(
            title=title,
            document_type=doc_type,
            source_url=source_url,
            citation=citation,
            date_enacted=dates.get("enacted"),
            date_commenced=dates.get("commenced"),
            date_last_amended=dates.get("amended"),
            published_at=dates.get("published"),
            raw_text=normalized_text,
            sections=sections if sections else None,
            content_hash=content_hash,
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract document title from HTML."""
        # Try various selectors
        selectors = [
            "h1",
            ".title",
            ".document-title",
            "title",
            "meta[property='og:title']",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True) or element.get("content", "")
                if title:
                    return title

        # Fallback: use URL or first heading
        first_h1 = soup.find("h1")
        if first_h1:
            return first_h1.get_text(strip=True)

        return "Untitled Document"

    def _extract_title_from_text(self, text: str) -> str:
        """Extract title from plain text."""
        lines = text.split("\n")
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and len(line) < 200:  # Reasonable title length
                # Check if it looks like a title (not a section)
                if not re.match(r"^(Section|Part|Division)\s+\d+", line, re.IGNORECASE):
                    return line
        return "Untitled Document"

    def _extract_citation(self, soup: BeautifulSoup, html_content: str) -> str | None:
        """Extract citation from HTML."""
        # Look for citation patterns in text
        citation_patterns = [
            r"Citation[:\s]+([A-Z0-9\s]+)",
            r"([A-Z]{2,}\s+\d+\s+of\s+\d{4})",  # e.g., "Act 15 of 2020"
            r"([A-Z]{2,}\s+No\.\s+\d+)",
        ]

        text = soup.get_text()
        for pattern in citation_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_citation_from_text(self, text: str) -> str | None:
        """Extract citation from plain text."""
        citation_patterns = [
            r"Citation[:\s]+([A-Z0-9\s]+)",
            r"([A-Z]{2,}\s+\d+\s+of\s+\d{4})",
            r"([A-Z]{2,}\s+No\.\s+\d+)",
        ]

        for pattern in citation_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_dates(self, soup: BeautifulSoup, html_content: str) -> dict[str, datetime | None]:
        """Extract dates from HTML."""
        text = soup.get_text()
        return self._extract_dates_from_text(text)

    def _extract_dates_from_text(self, text: str) -> dict[str, datetime | None]:
        """Extract dates from text content."""
        dates: dict[str, datetime | None] = {
            "enacted": None,
            "commenced": None,
            "amended": None,
            "published": None,
        }

        # Date patterns
        date_patterns = [
            r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
            r"(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})",
        ]

        # Keywords for different date types
        keywords = {
            "enacted": ["enacted", "passed", "assented"],
            "commenced": ["commenced", "effective", "in force"],
            "amended": ["amended", "revised", "updated"],
            "published": ["published", "gazetted"],
        }

        for date_type, keywords_list in keywords.items():
            for keyword in keywords_list:
                pattern = rf"{keyword}[:\s]+(?:on\s+)?({'|'.join(date_patterns)})"
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    date_str = match.group(1)
                    parsed_date = self._parse_date(date_str)
                    if parsed_date:
                        dates[date_type] = parsed_date
                        break

        return dates

    def _parse_date(self, date_str: str) -> datetime | None:
        """Parse a date string into datetime."""
        # Try common formats
        formats = [
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%d %B %Y",
            "%B %d, %Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        return None

    def _compute_hash(self, content: str) -> str:
        """Compute SHA256 hash of normalized content."""
        import hashlib

        normalized = content.strip().lower().replace("\r\n", "\n").replace("\r", "\n")
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

