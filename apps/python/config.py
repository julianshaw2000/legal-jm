"""Configuration management via environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    database_url: str
    openai_api_key: str | None = None
    log_level: str = "INFO"
    scrape_base_url_acts: str | None = None
    scrape_base_url_regulations: str | None = None
    scrape_base_url_cases: str | None = None
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_retries: int = 3
    retry_backoff_factor: float = 2.0

    @classmethod
    def from_env(cls) -> Config:
        """Load configuration from environment variables."""
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL environment variable is required")

        return cls(
            database_url=db_url,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            scrape_base_url_acts=os.getenv("SCRAPE_BASE_URL_ACTS"),
            scrape_base_url_regulations=os.getenv("SCRAPE_BASE_URL_REGULATIONS"),
            scrape_base_url_cases=os.getenv("SCRAPE_BASE_URL_CASES"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            embedding_dimensions=int(os.getenv("EMBEDDING_DIMENSIONS", "1536")),
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            retry_backoff_factor=float(os.getenv("RETRY_BACKOFF_FACTOR", "2.0")),
        )

