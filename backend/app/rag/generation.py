"""
DocuMind AI — Generation Service Interface
Sends the assembled context + question to an LLM and returns a grounded answer.

Phase 1 Status: INTERFACE STUB — returns a clear "not implemented" message.
Phase 2: Will integrate with OpenAI / Google Gemini API.

Integration point:
    Input:  question (str), context (str)
    Output: answer string (grounded in the provided context only)
    Used by: RAGPipeline

Hallucination control note:
    The system prompt explicitly instructs the LLM to:
    - Answer only from the provided context.
    - Not invent facts, dates, documents, or evidence.
    - Say "I could not find sufficient evidence" if context is insufficient.
"""

from app.core.logging_config import get_logger

logger = get_logger(__name__)

# This system prompt will govern all LLM responses.
# It is a core part of the hallucination control strategy.
SYSTEM_PROMPT = """You are DocuMind AI, an institutional knowledge assistant for a college.

Your job is to answer questions based ONLY on the document context provided below.

Rules you MUST follow:
1. Answer only from the provided context. Do not use any external knowledge.
2. Do not invent facts, dates, document names, or evidence.
3. Do not guess. If the context does not contain the answer, clearly say:
   "I could not find sufficient evidence in the indexed institutional documents."
4. When referencing information, note which document it came from (e.g., "According to [Document Name], ...").
5. Be concise and professional. This is an institutional system used during NAAC/NBA accreditation.
6. Never make up accreditation outcomes, criteria numbers, or evaluation results.

Context from indexed documents:
{context}

If the context is empty or does not address the question, state that no relevant evidence was found.
"""

NO_EVIDENCE_ANSWER = (
    "I could not find sufficient evidence in the indexed institutional documents "
    "to answer this question. Please ensure the relevant documents have been indexed, "
    "or contact the system administrator."
)


class GenerationService:
    """
    Calls an LLM to generate an answer grounded in the retrieved context.

    Phase 1: Returns the NO_EVIDENCE_ANSWER stub with a log warning.
    Phase 2: Implement with OpenAI ChatCompletion or Google Gemini API.

    Example future implementation:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
                {"role": "user", "content": question},
            ],
            temperature=0.1,  # Low temperature for factual accuracy
            max_tokens=1500,
        )
        return response.choices[0].message.content
    """

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or "gpt-4o-mini"
        logger.info("GenerationService initialized (model: %s) [STUB]", self.model_name)

    async def generate(self, question: str, context: str) -> str:
        """
        Generate a grounded answer from the LLM.

        Args:
            question: The user's natural-language question.
            context: Formatted context string from ContextBuilder.

        Returns:
            A text answer grounded in the provided context.
        """
        logger.debug("generate called [STUB] for question: %r", question[:80])

        if not context:
            return NO_EVIDENCE_ANSWER

        # TODO Phase 2: Replace with actual LLM API call
        # The SYSTEM_PROMPT and NO_EVIDENCE_ANSWER are production-ready.
        return (
            "[Phase 1 Stub] The generation service is not yet connected to an LLM. "
            f"Retrieved context was found for your question. "
            "Connect an LLM provider in Phase 2 to see generated answers."
        )
