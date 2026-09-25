"""
DocuMind AI — Embedding Service
Generates vector embeddings using OpenAI's text-embedding-3-small model.

Phase 2C: Real implementation replacing the Phase 1 stub.

Provider:   OpenAI Embeddings API
Model:      text-embedding-3-small
Dimension:  1536
Metric:     cosine (Pinecone index must be configured with metric="cosine")

Integration points:
    - embed_query()     → RAGPipeline (query-time)
    - embed_documents() → Ingestion pipeline (index-time, batched)

Design principles:
    - OpenAI client is constructed on first use (lazy-init) so that importing
      this module never fails even when OPENAI_API_KEY is empty (e.g. in tests).
    - Input validation raises ValueError before any API call.
    - Provider exceptions are caught, logged, and re-raised as EmbeddingError
      so callers only need to handle one exception type.
    - API key is read from settings — never hardcoded.
"""

from __future__ import annotations

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Embedding dimension constants — must match Pinecone index configuration
# ---------------------------------------------------------------------------

EMBEDDING_DIMENSION = 1536          # OpenAI text-embedding-3-small
EMBEDDING_MODEL = "text-embedding-3-small"
MAX_BATCH_SIZE = 100                # OpenAI recommended batch limit


class EmbeddingError(Exception):
    """Raised when the embedding provider returns an error or is unavailable."""


class EmbeddingService:
    """
    Wraps the OpenAI Embeddings API to produce vectors for query and documents.

    Provider: OpenAI — text-embedding-3-small
    Dimension: 1536
    Similarity metric: cosine

    Usage:
        service = EmbeddingService()
        vector = await service.embed_query("What are student mentoring activities?")
        vectors = await service.embed_documents(["chunk 1 text", "chunk 2 text"])

    Configuration (from .env):
        OPENAI_API_KEY     — required for live calls
        OPENAI_EMBEDDING_MODEL — defaults to "text-embedding-3-small"

    The client is lazily constructed on the first API call so that importing
    this module without a valid API key does not crash on startup.
    """

    EMBEDDING_DIMENSION = EMBEDDING_DIMENSION

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.openai_embedding_model or EMBEDDING_MODEL
        self._client = None          # lazy-initialised on first call
        logger.info(
            "EmbeddingService initialised (model=%s, dim=%d)",
            self.model_name,
            EMBEDDING_DIMENSION,
        )

    def _get_client(self):
        """Return the OpenAI async client, creating it on first use."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI  # type: ignore[import-untyped]
            except ImportError as exc:
                raise EmbeddingError(
                    "openai package is not installed. "
                    "Run: pip install openai==1.76.0"
                ) from exc

            if not settings.openai_api_key:
                raise EmbeddingError(
                    "OPENAI_API_KEY is not configured. "
                    "Set it in .env before using the embedding service."
                )
            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._client

    async def embed_query(self, text: str) -> list[float]:
        """
        Embed a single query string for similarity search.

        Args:
            text: Natural-language query to embed.

        Returns:
            A 1536-dimensional float vector.

        Raises:
            ValueError: If text is empty or whitespace-only.
            EmbeddingError: If the OpenAI API call fails.
        """
        if not text or not text.strip():
            raise ValueError("embed_query: text must not be empty.")

        cleaned = text.strip()
        logger.debug("embed_query: model=%s text_len=%d", self.model_name, len(cleaned))

        try:
            client = self._get_client()
            response = await client.embeddings.create(
                model=self.model_name,
                input=cleaned,
            )
            vector = response.data[0].embedding
            logger.debug("embed_query: received vector of dim=%d", len(vector))
            return vector
        except EmbeddingError:
            raise
        except Exception as exc:
            logger.error("embed_query failed: %s", str(exc), exc_info=True)
            raise EmbeddingError(f"Embedding API error: {exc}") from exc

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a batch of document chunks for indexing into Pinecone.

        Batches up to MAX_BATCH_SIZE texts per API call to stay within
        OpenAI rate limits.

        Args:
            texts: List of text strings. Each must be non-empty.

        Returns:
            List of 1536-dimensional float vectors, one per input text.
            Order is preserved.

        Raises:
            ValueError: If texts is empty, or any text in the batch is empty.
            EmbeddingError: If the OpenAI API call fails.
        """
        if not texts:
            raise ValueError("embed_documents: texts list must not be empty.")

        empty_indices = [i for i, t in enumerate(texts) if not t or not t.strip()]
        if empty_indices:
            raise ValueError(
                f"embed_documents: texts at indices {empty_indices} are empty."
            )

        logger.debug(
            "embed_documents: model=%s doc_count=%d", self.model_name, len(texts)
        )

        all_vectors: list[list[float]] = []

        try:
            client = self._get_client()

            # Process in batches to stay within API limits
            for batch_start in range(0, len(texts), MAX_BATCH_SIZE):
                batch = texts[batch_start : batch_start + MAX_BATCH_SIZE]
                response = await client.embeddings.create(
                    model=self.model_name,
                    input=batch,
                )
                # OpenAI returns embeddings in the same order as input
                batch_vectors = [item.embedding for item in response.data]
                all_vectors.extend(batch_vectors)

            logger.debug(
                "embed_documents: produced %d vectors of dim=%d",
                len(all_vectors),
                len(all_vectors[0]) if all_vectors else 0,
            )
            return all_vectors

        except EmbeddingError:
            raise
        except Exception as exc:
            logger.error("embed_documents failed: %s", str(exc), exc_info=True)
            raise EmbeddingError(f"Embedding API error: {exc}") from exc


# ---------------------------------------------------------------------------
# Protocol for type-checking and testing with mock implementations
# ---------------------------------------------------------------------------

class EmbeddingServiceProtocol:
    """
    Protocol defining the embedding service interface.
    Use this type for dependency injection in the RAG pipeline and tests.
    """

    async def embed_query(self, text: str) -> list[float]:
        """Embed a single query string for retrieval."""
        raise NotImplementedError

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of document texts for indexing."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Module-level singleton — lazy, created on first use
# ---------------------------------------------------------------------------

_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """
    Return the configured EmbeddingService singleton.

    The singleton is created on first call. This means:
    - No OpenAI client is created at import time.
    - Tests can safely import this module without needing an API key.
    - Tests that need to control the service can inject a mock via
      RAGPipeline(embedding_service=MockEmbeddingService()).
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
