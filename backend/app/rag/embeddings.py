"""
DocuMind AI — Embedding Service Interface
Generates vector embeddings for text using a configured model.

Phase 1 Status: INTERFACE STUB — not connected to any model.
Phase 2: Will integrate with OpenAI text-embedding-3-small or equivalent.

Integration point:
    Input:  text string or list of strings
    Output: list of float vectors (embeddings)
    Used by: RAGPipeline (query embedding), ingestion pipeline (document chunks)
"""

from typing import Protocol

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingServiceProtocol(Protocol):
    """Protocol defining the embedding service interface."""

    async def embed_query(self, text: str) -> list[float]:
        """Embed a single query string for retrieval."""
        ...

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of document texts for indexing."""
        ...


class EmbeddingService:
    """
    Embedding service that wraps a configured embedding model.

    Phase 1: Returns a placeholder (zeros) so the RAG pipeline structure
    can be tested without a live API key.
    Phase 2: Replace with actual OpenAI / Gemini embedding call.

    Example future usage:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.embeddings.create(
            model=settings.openai_embedding_model,
            input=text,
        )
        return response.data[0].embedding
    """

    EMBEDDING_DIMENSION = 1536  # OpenAI text-embedding-3-small dimension

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or "text-embedding-3-small"
        logger.info("EmbeddingService initialized (model: %s) [STUB]", self.model_name)

    async def embed_query(self, text: str) -> list[float]:
        """
        Embed a single query for similarity search.

        Phase 1: Returns zero vector. Replace with live API call in Phase 2.

        Args:
            text: The query string to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        logger.debug("embed_query called [STUB] for text: %r", text[:80])
        # TODO Phase 2: Replace with actual embedding API call
        return [0.0] * self.EMBEDDING_DIMENSION

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a batch of document chunks for indexing.

        Phase 1: Returns zero vectors. Replace with live API call in Phase 2.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors, one per input text.
        """
        logger.debug("embed_documents called [STUB] for %d texts", len(texts))
        # TODO Phase 2: Replace with actual embedding API call (batched)
        return [[0.0] * self.EMBEDDING_DIMENSION for _ in texts]


# Module-level singleton (will be replaced with DI in Phase 2)
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Return the configured embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
