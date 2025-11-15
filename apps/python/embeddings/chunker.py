"""Text chunking utilities for embeddings."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection

from ..config import Config


class ChunkingService:
    """Service for chunking documents and managing chunks."""

    def __init__(self, config: Config, conn: Connection) -> None:
        """Initialize chunking service."""
        self.config = config
        self.conn = conn
        self.chunk_size = config.chunk_size
        self.chunk_overlap = config.chunk_overlap

    def chunk_text(self, text: str, preserve_sentences: bool = True) -> list[str]:
        """Split text into chunks of appropriate size."""
        if preserve_sentences:
            # Split by sentences first
            sentences = re.split(r"(?<=[.!?])\s+", text)
            chunks: list[str] = []
            current_chunk: list[str] = []

            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                # Check if adding this sentence would exceed chunk size
                current_text = " ".join(current_chunk)
                if len(current_text) + len(sentence) + 1 > self.chunk_size and current_chunk:
                    # Save current chunk
                    chunks.append(current_text)
                    # Start new chunk with overlap
                    if self.chunk_overlap > 0 and current_chunk:
                        overlap_text = " ".join(current_chunk[-2:]) if len(current_chunk) >= 2 else current_text
                        current_chunk = [overlap_text[-self.chunk_overlap :]] if len(overlap_text) > self.chunk_overlap else [overlap_text]
                    else:
                        current_chunk = []

                current_chunk.append(sentence)

            # Add final chunk
            if current_chunk:
                chunks.append(" ".join(current_chunk))

            return chunks if chunks else [text]
        else:
            # Simple character-based chunking
            chunks = []
            start = 0
            while start < len(text):
                end = start + self.chunk_size
                chunk = text[start:end]
                chunks.append(chunk)
                start = end - self.chunk_overlap
            return chunks

    def create_chunks_for_document(self, document_id: str) -> list[str]:
        """Create chunks for a document and return chunk IDs."""
        # Get all sections for the document
        sections = self.conn.execute(
            text(
                """
                SELECT id, text, index
                FROM "Section"
                WHERE "documentId" = :document_id
                ORDER BY index
                """
            ),
            {"document_id": document_id},
        ).fetchall()

        chunk_ids: list[str] = []

        for section_id, section_text, section_index in sections:
            # Chunk the section text
            chunks = self.chunk_text(section_text)

            # Insert chunks
            for chunk_index, chunk_text in enumerate(chunks):
                # Check if chunk already exists
                existing = self.conn.execute(
                    text(
                        """
                        SELECT id FROM "Chunk"
                        WHERE "documentId" = :document_id
                        AND "sectionId" = :section_id
                        AND index = :chunk_index
                        """
                    ),
                    {
                        "document_id": document_id,
                        "section_id": section_id,
                        "chunk_index": chunk_index,
                    },
                ).fetchone()

                if existing:
                    chunk_ids.append(existing[0])
                else:
                    # Create new chunk
                    result = self.conn.execute(
                        text(
                            """
                            INSERT INTO "Chunk" (
                                id, "documentId", "sectionId", index, text, "createdAt"
                            )
                            VALUES (
                                gen_random_uuid()::text,
                                :document_id,
                                :section_id,
                                :chunk_index,
                                :text,
                                NOW()
                            )
                            RETURNING id
                            """
                        ),
                        {
                            "document_id": document_id,
                            "section_id": section_id,
                            "chunk_index": chunk_index,
                            "text": chunk_text,
                        },
                    )
                    chunk_ids.append(result.fetchone()[0])

        return chunk_ids

    def get_chunks_without_embeddings(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get chunks that don't have embeddings yet."""
        results = self.conn.execute(
            text(
                """
                SELECT c.id, c."documentId", c."sectionId", c.index, c.text
                FROM "Chunk" c
                LEFT JOIN "Embedding" e ON e."chunkId" = c.id
                WHERE e.id IS NULL
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).fetchall()

        return [
            {
                "id": row[0],
                "document_id": row[1],
                "section_id": row[2],
                "index": row[3],
                "text": row[4],
            }
            for row in results
        ]

