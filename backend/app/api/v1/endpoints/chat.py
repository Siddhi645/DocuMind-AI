"""
DocuMind AI — Chat Endpoint
POST /api/chat
GET  /api/chat/history
GET  /api/chat/{session_id}

Phase 1 Status:
- POST /api/chat: Wired to RAGPipeline (stubs return placeholder answers).
- GET endpoints: Schema-defined stubs.
Phase 2: Connect RAGPipeline to live Pinecone + LLM. Persist sessions to PostgreSQL.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import CurrentUser, get_current_user
from app.core.logging_config import get_logger
from app.rag.pipeline import get_rag_pipeline
from app.schemas.chat import ChatRequest, ChatResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Ask a question",
    description=(
        "Submit a natural-language question. The system retrieves relevant institutional "
        "documents and generates a grounded answer with source citations."
    ),
)
async def ask_question(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ChatResponse:
    """
    Core RAG endpoint.

    Flow:
    1. Validate and extract question + filters from request body.
    2. Build permission-aware Pinecone metadata filter from the user's JWT claims.
    3. Embed the question, retrieve chunks, build context, generate answer.
    4. Return grounded answer with source citations.

    Phase 1: RAGPipeline is wired but all components return stubs.
             Endpoint is authenticated via JWT.
    Phase 2: Live Pinecone + LLM.
    """
    logger.info(
        "Chat request from user=%s role=%s question=%r",
        current_user.user_id,
        current_user.role,
        request.question[:80],
    )

    try:
        pipeline = get_rag_pipeline()
        session_id = request.session_id or str(uuid.uuid4())

        response = await pipeline.run(
            question=request.question,
            user_role=current_user.role,
            user_department=None,  # TODO Phase 2: Load from user's DB record
            client_filters=request.filters,
            session_id=session_id,
        )
        return response

    except Exception as exc:
        logger.error("Chat pipeline error: %s", str(exc), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "PIPELINE_ERROR",
                "message": "The AI service encountered an error. Please try again.",
            },
        )


@router.get(
    "/history",
    summary="Get chat history",
    description="Returns the authenticated user's past chat sessions.",
)
async def get_chat_history(
    current_user: CurrentUser = Depends(get_current_user),
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """
    Phase 1 stub: Returns empty history.
    Phase 2: Query PostgreSQL for user's ChatSession + Message records.
    """
    # TODO Phase 2: Query db for current_user.user_id's sessions
    return {
        "sessions": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
        "message": "[Phase 1] Chat history will be available after database integration.",
    }


@router.get(
    "/{session_id}",
    summary="Get a chat session",
    description="Returns messages for a specific chat session.",
)
async def get_chat_session(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict:
    """
    Phase 1 stub.
    Phase 2: Fetch session + messages from PostgreSQL, verify ownership.
    """
    # TODO Phase 2: Fetch session from DB and verify current_user owns it
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "error": "NOT_IMPLEMENTED",
            "message": "Session retrieval will be available after database integration.",
        },
    )
