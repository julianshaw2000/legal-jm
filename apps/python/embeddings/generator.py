"""Generate embeddings for text chunks."""

from __future__ import annotations

import logging
from typing import Any

from openai import OpenAI

from ..config import Config

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings using OpenAI API."""

    def __init__(self, config: Config) -> None:
        """Initialize embedding generator."""
        self.config = config
        self.client: OpenAI | None = None

        if config.openai_api_key:
            self.client = OpenAI(api_key=config.openai_api_key)
        else:
            logger.warning("OpenAI API key not configured - embeddings will be skipped")

    def generate_embedding(self, text: str) -> list[float] | None:
        """Generate embedding for a text chunk."""
        if not self.client:
            logger.warning("OpenAI client not available - skipping embedding generation")
            return None

        try:
            response = self.client.embeddings.create(
                model=self.config.embedding_model,
                input=text,
                dimensions=self.config.embedding_dimensions,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None

    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float] | None]:
        """Generate embeddings for multiple texts."""
        if not self.client:
            return [None] * len(texts)

        results: list[list[float] | None] = []
        # Process in batches to avoid rate limits
        batch_size = 100

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                response = self.client.embeddings.create(
                    model=self.config.embedding_model,
                    input=batch,
                    dimensions=self.config.embedding_dimensions,
                )
                batch_results = [item.embedding for item in response.data]
                results.extend(batch_results)
            except Exception as e:
                logger.error(f"Failed to generate batch embeddings: {e}")
                results.extend([None] * len(batch))

        return results

