"""Document normalization and cleaning utilities."""

from __future__ import annotations

import re
from html import unescape

from bs4 import BeautifulSoup


class DocumentNormalizer:
    """Normalizes and cleans raw HTML/text content."""

    @staticmethod
    def clean_html(html_content: str) -> str:
        """Extract and clean text from HTML."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove script, style, and other non-content elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside", "ad"]):
            element.decompose()

        # Extract text
        text = soup.get_text(separator="\n", strip=True)

        # Normalize whitespace
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)  # Multiple blank lines to double
        text = re.sub(r"[ \t]+", " ", text)  # Multiple spaces to single
        text = text.strip()

        return text

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize plain text content."""
        # Decode HTML entities
        text = unescape(text)

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Normalize whitespace
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = text.strip()

        return text

    @staticmethod
    def extract_sections(text: str) -> list[tuple[int, str | None, str]]:
        """
        Extract sections from text based on common patterns.

        Returns list of (index, heading, text) tuples.
        """
        sections: list[tuple[int, str | None, str]] = []
        lines = text.split("\n")

        current_section: list[str] = []
        current_heading: str | None = None
        index = 0

        # Patterns for section headings
        section_patterns = [
            r"^Section\s+(\d+[A-Za-z]?)\s*[:.]?\s*(.*)$",
            r"^(\d+[A-Za-z]?)[\.\)]\s+(.+)$",
            r"^Part\s+([IVX]+|[A-Z])\s*[:.]?\s*(.*)$",
            r"^Division\s+(\d+[A-Za-z]?)\s*[:.]?\s*(.*)$",
            r"^Subsection\s+\((\d+[a-z]?)\)\s*[:.]?\s*(.*)$",
        ]

        for line in lines:
            line = line.strip()
            if not line:
                if current_section:
                    current_section.append("")
                continue

            # Check if line matches a section heading pattern
            matched = False
            for pattern in section_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    # Save previous section
                    if current_section:
                        sections.append((index, current_heading, "\n".join(current_section)))
                        index += 1

                    # Start new section
                    current_heading = match.group(-1).strip() if match.lastindex >= 2 else None
                    current_section = []
                    matched = True
                    break

            if not matched:
                current_section.append(line)

        # Add final section
        if current_section:
            sections.append((index, current_heading, "\n".join(current_section)))

        # If no sections found, treat entire text as one section
        if not sections:
            sections.append((0, None, text))

        return sections

