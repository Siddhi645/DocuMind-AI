"""
DocuMind AI — Context Builder
Assembles retrieved document chunks into a prompt-ready context string.

Phase 1 Status: INTERFACE STUB — returns placeholder context.
Phase 2: Will implement chunk selection, deduplication, and token counting.

Integration point:
    Input:  list[RetrievedChunk]
    Output: formatted context string for LLM prompt
    Used by: RAGPipeline → GenerationService
"""

from app.core.logging_config import get_logger
from app.rag.retrieval import RetrievedChunk

logger = get_logger(__name__)

# Maximum number of characters to include in LLM context
# Prevents exceeding LLM context window limits
MAX_CONTEXT_CHARS = 12_000


class ContextBuilder:
    """
    Selects and formats retrieved chunks into an LLM-ready context string.

    Responsibilities:
    - Select the most relevant chunks within token/char limits
    - Format each chunk with its source metadata
    - Deduplicate overlapping content
    - Produce a structured prompt context section

    Phase 1: Returns a formatted placeholder.
    Phase 2: Implement token-aware selection and deduplication.
    """

    def __init__(self, max_context_chars: int = MAX_CONTEXT_CHARS):
        self.max_context_chars = max_context_chars
        logger.info("ContextBuilder initialized (max_chars=%d)", max_context_chars)

    def build(self, chunks: list[RetrievedChunk]) -> str:
        """
        Build a context string from retrieved chunks.

        Args:
            chunks: Ranked list of RetrievedChunk from RetrievalService.

        Returns:
            A formatted string to include in the LLM prompt.
        """
        if not chunks:
            logger.debug("ContextBuilder: no chunks to build context from.")
            return ""

        context_parts: list[str] = []
        total_chars = 0

        for i, chunk in enumerate(chunks, start=1):
            # Format source header
            source_header = f"[Source {i}: {chunk.document_name}"
            if chunk.page:
                source_header += f", Page {chunk.page}"
            if chunk.section:
                source_header += f", Section: {chunk.section}"
            source_header += "]"

            chunk_text = f"{source_header}\n{chunk.text}\n"

            if total_chars + len(chunk_text) > self.max_context_chars:
                logger.debug("Context limit reached at chunk %d.", i)
                break

            context_parts.append(chunk_text)
            total_chars += len(chunk_text)

        logger.debug("Built context from %d chunks (%d chars).", len(context_parts), total_chars)
        return "\n---\n".join(context_parts)
