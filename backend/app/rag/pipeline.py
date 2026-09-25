"""
DocuMind AI — RAG Pipeline
Orchestrates the complete question-answering flow.

Phase 1 Status: STRUCTURE COMPLETE — all steps defined.
                Embedding and retrieval return stubs.
                Generation returns a placeholder.
Phase 2: Connect EmbeddingService, RetrievalService, GenerationService to live APIs.

Pipeline:
    Question
       ↓
    Query preprocessing
       ↓
    Permission / metadata filter construction (from user's role + filters)
       ↓
    Query embedding (EmbeddingService)
       ↓
    Pinecone similarity search (RetrievalService)
       ↓
    Context building (ContextBuilder)
       ↓
    LLM generation (GenerationService)
       ↓
    Citation formatting (CitationFormatter)
       ↓
    ChatResponse

Security: Metadata filters are built from the authenticated user's permissions —
not from the client request. This prevents unauthorized retrieval.
"""

from typing import Any

from app.core.logging_config import get_logger
from app.rag.citations import CitationFormatter
from app.rag.context import ContextBuilder
from app.rag.embeddings import EmbeddingError, EmbeddingService, get_embedding_service
from app.rag.generation import GenerationService
from app.rag.retrieval import RetrievalError, RetrievalService, get_retrieval_service
from app.schemas.chat import ChatFilters, ChatResponse, SourceCitation

logger = get_logger(__name__)


class RAGPipeline:
    """
    Orchestrates the full RAG pipeline for a single user query.

    Dependencies are injected to allow testing each component independently.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        retrieval_service: RetrievalService | None = None,
        generation_service: GenerationService | None = None,
        context_builder: ContextBuilder | None = None,
        citation_formatter: CitationFormatter | None = None,
    ):
        self.embedding_service = embedding_service or get_embedding_service()
        self.retrieval_service = retrieval_service or get_retrieval_service()
        self.generation_service = generation_service or GenerationService()
        self.context_builder = context_builder or ContextBuilder()
        self.citation_formatter = citation_formatter or CitationFormatter()

    def _build_metadata_filter(
        self,
        user_role: str,
        user_department: str | None,
        client_filters: ChatFilters | None,
    ) -> dict[str, Any]:
        """
        Construct Pinecone metadata filter from user permissions + optional client filters.

        Security principle: The backend ALWAYS determines allowed access levels.
        The client may request additional filters (e.g., department) but cannot
        override the permission-based access_level filter.

        Args:
            user_role: Authenticated user's role (admin, faculty, staff, student).
            user_department: The user's department for department-scoped access.
            client_filters: Optional filters from the chat request body.

        Returns:
            Pinecone-compatible filter dict.
        """
        # Role → allowed access levels (hierarchical)
        role_access_map = {
            "admin": ["public", "student", "faculty", "admin"],
            "faculty": ["public", "student", "faculty"],
            "staff": ["public", "faculty"],
            "student": ["public", "student"],
        }
        allowed_levels = role_access_map.get(user_role, ["public"])

        pinecone_filter: dict[str, Any] = {
            "access_level": {"$in": allowed_levels}
        }

        # Add optional client-requested filters (these narrow, never widen, access)
        if client_filters:
            if client_filters.department:
                pinecone_filter["department"] = client_filters.department
            if client_filters.academic_year:
                pinecone_filter["academic_year"] = client_filters.academic_year
            if client_filters.document_type:
                pinecone_filter["document_type"] = client_filters.document_type

        return pinecone_filter

    async def run(
        self,
        question: str,
        user_role: str = "faculty",
        user_department: str | None = None,
        client_filters: ChatFilters | None = None,
        session_id: str | None = None,
    ) -> ChatResponse:
        """
        Execute the full RAG pipeline for a question.

        Args:
            question: The user's natural-language question.
            user_role: Authenticated user's role (from JWT).
            user_department: User's department (for scoped access).
            client_filters: Optional metadata filters from the request body.
            session_id: Optional chat session ID for conversation continuity.

        Returns:
            ChatResponse with answer, sources, and session information.
        """
        logger.info("RAG pipeline started for question: %r", question[:80])

        # Step 1: Preprocess query
        processed_question = question.strip()

        # Step 2: Build permission-aware metadata filter
        metadata_filter = self._build_metadata_filter(
            user_role=user_role,
            user_department=user_department,
            client_filters=client_filters,
        )
        logger.debug("Metadata filter constructed: %s", metadata_filter)

        try:
            # Step 3: Embed the query
            query_embedding = await self.embedding_service.embed_query(processed_question)

            # Step 4: Retrieve relevant chunks from Pinecone
            chunks = await self.retrieval_service.retrieve(
                query_embedding=query_embedding,
                metadata_filter=metadata_filter,
            )
            logger.info("Retrieved %d chunks from knowledge base.", len(chunks))

        except EmbeddingError as exc:
            logger.warning("Embedding service unavailable: %s", str(exc))
            return ChatResponse(
                success=False,
                answer="The AI embedding service is not available. Please contact the administrator.",
                sources=[],
                session_id=session_id,
                question=processed_question,
            )
        except RetrievalError as exc:
            logger.warning("Retrieval service unavailable: %s", str(exc))
            return ChatResponse(
                success=False,
                answer="The document retrieval service is not available. Please contact the administrator.",
                sources=[],
                session_id=session_id,
                question=processed_question,
            )

        # Step 5: Build context for LLM
        context = self.context_builder.build(chunks)

        # Step 6: Generate grounded answer
        answer = await self.generation_service.generate(
            question=processed_question,
            context=context,
        )

        # Step 7: Format citations
        citations = self.citation_formatter.format(chunks)

        logger.info("RAG pipeline complete. Sources: %d", len(citations))

        return ChatResponse(
            success=True,
            answer=answer,
            sources=citations,
            session_id=session_id,
            question=processed_question,
        )


# Module-level singleton for use in API endpoints
_rag_pipeline: RAGPipeline | None = None


def get_rag_pipeline() -> RAGPipeline:
    """Return the configured RAGPipeline instance."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
