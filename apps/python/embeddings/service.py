"""Service for managing embeddings."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection

from ..config import Config
from .chunker import ChunkingService
from .generator import EmbeddingGenerator

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and storing embeddings."""

    def __init__(self, config: Config, conn: Connection) -> None:
        """Initialize embedding service."""
        self.config = config
        self.conn = conn
        self.generator = EmbeddingGenerator(config)
        self.chunker = ChunkingService(config, conn)

    def process_document_chunks(self, document_id: str) -> int:
        """Create chunks and generate embeddings for a document."""
        # Create chunks if they don't exist
        chunk_ids = self.chunker.create_chunks_for_document(document_id)

        # Generate embeddings for chunks without them
        processed = 0
        for chunk_id in chunk_ids:
            # Check if embedding exists
            existing = self.conn.execute(
                text('SELECT id FROM "Embedding" WHERE "chunkId" = :chunk_id'),
                {"chunk_id": chunk_id},
            ).fetchone()

            if existing:
                continue

            # Get chunk text
            chunk = self.conn.execute(
                text('SELECT text FROM "Chunk" WHERE id = :chunk_id'),
                {"chunk_id": chunk_id},
            ).fetchone()

            if not chunk:
                continue

            # Generate embedding
            embedding = self.generator.generate_embedding(chunk[0])
            if embedding:
                # Store embedding (using pgvector)
                self.conn.execute(
                    text(
                        """
                        INSERT INTO "Embedding" (id, "chunkId", vector)
                        VALUES (
                            gen_random_uuid()::text,
                            :chunk_id,
                            :vector::vector
                        )
                        ON CONFLICT ("chunkId") DO UPDATE
                        SET vector = EXCLUDED.vector
                        """
                    ),
                    {
                        "chunk_id": chunk_id,
                        "vector": f"[{','.join(map(str, embedding))}]",
                    },
                )
                processed += 1

        return processed

    def update_all_embeddings(self, batch_size: int = 100) -> dict[str, int]:
        """Update embeddings for all chunks that don't have them."""
        stats = {"processed": 0, "failed": 0, "skipped": 0}

        while True:
            chunks = self.chunker.get_chunks_without_embeddings(batch_size)
            if not chunks:
                break

            for chunk in chunks:
                try:
                    embedding = self.generator.generate_embedding(chunk["text"])
                    if embedding:
                        self.conn.execute(
                            text(
                                """
                                INSERT INTO "Embedding" (id, "chunkId", vector)
                                VALUES (
                                    gen_random_uuid()::text,
                                    :chunk_id,
                                    :vector::vector
                                )
                                ON CONFLICT ("chunkId") DO UPDATE
                                SET vector = EXCLUDED.vector
                                """
                            ),
                            {
                                "chunk_id": chunk["id"],
                                "vector": f"[{','.join(map(str, embedding))}]",
                            },
                        )
                        stats["processed"] += 1
                    else:
                        stats["skipped"] += 1
                except Exception as e:
                    logger.error(f"Failed to process chunk {chunk['id']}: {e}")
                    stats["failed"] += 1

            self.conn.commit()

        return stats

