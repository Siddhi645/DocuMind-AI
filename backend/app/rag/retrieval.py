"""
DocuMind AI — Retrieval Service Interface
Handles Pinecone vector similarity search with metadata filtering.

Phase 1 Status: INTERFACE STUB — not connected to Pinecone.
Phase 2: Will integrate with the Pinecone Python SDK.

Integration point:
    Input:  query embedding (list[float]), metadata filters, top_k
    Output: list of RetrievedChunk objects with metadata + score
    Used by: RAGPipeline
"""

from dataclasses import dataclass, field
from typing import Any

from app.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class RetrievedChunk:
    """
    A document chunk retrieved from Pinecone.
    Contains the text content and all metadata needed for citation.

    This is the core data structure flowing through the RAG pipeline.
    """
    chunk_id: str
    text: str
    score: float
    document_id: str = ""
    document_name: str = ""
    department: str = ""
    academic_year: str = ""
    page: int | None = None
    section: str | None = None
    access_level: str = "faculty"
    metadata: dict[str, Any] = field(default_factory=dict)


class RetrievalService:
    """
    Retrieves semantically relevant document chunks from Pinecone.

    Phase 1: Returns an empty list (no Pinecone connection).
    Phase 2: Replace with:
        from pinecone import Pinecone
        pc = Pinecone(api_key=settings.pinecone_api_key)
        index = pc.Index(settings.pinecone_index_name)
        results = index.query(
            vector=query_embedding,
            filter=metadata_filter,
            top_k=top_k,
            include_metadata=True,
        )

    Security note:
        Metadata filters are constructed by the backend based on the
        authenticated user's role and department — NOT by the client.
        This prevents unauthorized document retrieval.
    """

    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        logger.info("RetrievalService initialized (top_k=%d) [STUB]", top_k)

    async def retrieve(
        self,
        query_embedding: list[float],
        metadata_filter: dict[str, Any] | None = None,
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        """
        Retrieve the most semantically similar document chunks.

        Args:
            query_embedding: Vector from EmbeddingService.embed_query().
            metadata_filter: Pinecone metadata filter dict.
                             Built by backend from user permissions — never from client.
            top_k: Number of chunks to retrieve. Defaults to self.top_k.

        Returns:
            List of RetrievedChunk objects sorted by relevance score (descending).
        """
        k = top_k or self.top_k
        logger.debug(
            "retrieve called [STUB]: top_k=%d, filter=%s", k, metadata_filter
        )
        # TODO Phase 2: Replace with actual Pinecone query
        return []

    async def delete_document_chunks(self, document_id: str) -> int:
        """
        Delete all Pinecone vectors belonging to a document.
        Used during document update and deletion workflows.

        Args:
            document_id: The document's UUID.

        Returns:
            Number of vectors deleted.
        """
        logger.debug("delete_document_chunks called [STUB] for document_id=%s", document_id)
        # TODO Phase 2: index.delete(filter={"document_id": document_id})
        return 0

    async def upsert_chunks(
        self,
        chunks: list[dict[str, Any]],
    ) -> int:
        """
        Upsert document chunk vectors into Pinecone.
        Used by the ingestion pipeline.

        Args:
            chunks: List of dicts with keys: id, values (embedding), metadata.

        Returns:
            Number of vectors upserted.
        """
        logger.debug("upsert_chunks called [STUB] for %d chunks", len(chunks))
        # TODO Phase 2: index.upsert(vectors=chunks)
        return 0
