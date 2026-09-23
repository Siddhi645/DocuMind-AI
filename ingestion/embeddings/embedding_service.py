"""
DocuMind AI — Ingestion Embedding Service
Generates embeddings for document chunks during ingestion.

Phase 1 Status: INTERFACE STUB
Phase 2: Connect to OpenAI text-embedding-3-small or equivalent.

Note: This is a separate module from backend/app/rag/embeddings.py.
The ingestion pipeline runs independently of the backend application.
Both use the same embedding model for consistency.

Integration point:
    Input:  list[TextChunk]
    Output: list of (chunk_id, embedding_vector, metadata) tuples for Pinecone upsert
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger("documind.ingestion.embeddings")

# Must match the model used in backend/app/rag/embeddings.py
# If you change the model, re-index all documents.
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536


@dataclass
class EmbeddedChunk:
    """A document chunk with its embedding vector, ready for Pinecone upsert."""
    chunk_id: str
    embedding: list[float]
    metadata: dict


class IngestionEmbeddingService:
    """
    Generates embeddings for document chunks during ingestion.

    Phase 1: Returns zero vectors.
    Phase 2: Batch-call OpenAI (or configured provider) with retry and rate limiting.

    Important efficiency note (from context.md):
    - Embeddings are generated ONCE per document during ingestion.
    - They are NOT regenerated for every user query.
    - Only query embeddings are generated at query time.
    """

    def __init__(self, model: str = EMBEDDING_MODEL, batch_size: int = 100):
        self.model = model
        self.batch_size = batch_size
        logger.info(
            "IngestionEmbeddingService initialized (model=%s, batch_size=%d) [STUB]",
            model, batch_size
        )

    def embed_chunks(
        self, chunks: list, metadata_list: list[dict]
    ) -> list[EmbeddedChunk]:
        """
        Generate embeddings for a list of TextChunks.

        Args:
            chunks: List of TextChunk objects from TextChunker.
            metadata_list: Corresponding Pinecone metadata dicts from MetadataBuilder.

        Returns:
            List of EmbeddedChunk objects ready for Pinecone upsert.
        """
        if not chunks:
            return []

        logger.info(
            "Embedding %d chunks (model=%s) [STUB]", len(chunks), self.model
        )

        results: list[EmbeddedChunk] = []
        for chunk, metadata in zip(chunks, metadata_list):
            # TODO Phase 2: Replace with batched OpenAI embedding call
            # Process in self.batch_size groups to respect API limits
            zero_vector = [0.0] * EMBEDDING_DIMENSION
            results.append(EmbeddedChunk(
                chunk_id=chunk.chunk_id,
                embedding=zero_vector,
                metadata=metadata,
            ))

        logger.info("Embedded %d chunks [STUB]", len(results))
        return results

    def format_for_pinecone(self, embedded_chunks: list[EmbeddedChunk]) -> list[dict]:
        """
        Format EmbeddedChunks as Pinecone upsert records.

        Returns:
            List of dicts: {"id": str, "values": list[float], "metadata": dict}
        """
        return [
            {
                "id": ec.chunk_id,
                "values": ec.embedding,
                "metadata": ec.metadata,
            }
            for ec in embedded_chunks
        ]
