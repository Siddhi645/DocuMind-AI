"""
DocuMind AI — Chat schemas
Request/response models for the core chat/RAG endpoint.
This contract is the primary integration point between frontend and backend.
"""

from typing import Any
from pydantic import BaseModel, field_validator


class ChatFilters(BaseModel):
    """
    Optional filters to narrow document retrieval.
    These map to Pinecone metadata filters during retrieval.

    Security note: access_level is intentionally NOT a client-supplied field.
    The backend always derives access_level from the authenticated user's role
    in RAGPipeline._build_metadata_filter(). Allowing the client to supply
    access_level would bypass the permission model (context.md §18).
    """
    department: str | None = None
    academic_year: str | None = None
    document_type: str | None = None


class ChatRequest(BaseModel):
    """
    Incoming question from the frontend.

    Corresponds to:
        POST /api/chat
    """
    question: str
    filters: ChatFilters | None = None
    session_id: str | None = None  # Optional: continue an existing session

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Question must not be empty.")
        if len(v) > 2000:
            raise ValueError("Question must not exceed 2000 characters.")
        return v.strip()


class SourceCitation(BaseModel):
    """
    A single source document cited in the answer.
    Contains enough information to trace back to the original document.
    """
    document_name: str
    document_id: str | None = None
    page: int | None = None
    section: str | None = None
    snippet: str | None = None
    academic_year: str | None = None
    department: str | None = None
    score: float | None = None  # Relevance score from retrieval


class ChatResponse(BaseModel):
    """
    Response from the chat endpoint.

    success=True with empty sources → no relevant documents found
    success=False → system error

    Corresponds to:
        POST /api/chat → 200 OK
    """
    success: bool
    answer: str
    sources: list[SourceCitation] = []
    session_id: str | None = None
    question: str | None = None


class ErrorResponse(BaseModel):
    """Standard error response for all API errors."""
    success: bool = False
    error: str
    message: str
    details: Any | None = None
