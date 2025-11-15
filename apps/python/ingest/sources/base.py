"""Base classes for document sources."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any

import httpx

from ...config import Config
from ...models import DocumentType, ParsedDocument, ScrapeResult


class BaseScraper(ABC):
    """Base class for document scrapers."""

    def __init__(self, config: Config, source_name: str) -> None:
        """Initialize scraper with configuration."""
        self.config = config
        self.source_name = source_name
        self.client = httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; LegalIngestor/1.0)",
            },
        )

    @abstractmethod
    def scrape(self) -> ScrapeResult:
        """Scrape documents from this source."""
        pass

    def fetch_url(self, url: str, retries: int | None = None) -> str:
        """Fetch content from URL with retries."""
        if retries is None:
            retries = self.config.max_retries

        last_error: Exception | None = None
        for attempt in range(retries):
            try:
                response = self.client.get(url)
                response.raise_for_status()
                return response.text
            except httpx.HTTPError as e:
                last_error = e
                if attempt < retries - 1:
                    wait_time = self.config.retry_backoff_factor ** attempt
                    time.sleep(wait_time)
                else:
                    raise

        if last_error:
            raise last_error
        return ""

    def close(self) -> None:
        """Close HTTP client."""
        self.client.close()

    def __enter__(self) -> BaseScraper:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

