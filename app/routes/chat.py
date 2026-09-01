"""
chat.py  (app/routes/chat.py)
------------------------------
Route: POST /api/chat

This is where the full RAG pipeline comes together.

RAG = Retrieval-Augmented Generation
  Instead of asking the LLM to answer from memory, we first RETRIEVE relevant
  context from ChromaDB (our vector database), AUGMENT the user's question with
  that context, and then GENERATE a grounded answer using the LLM.

The three steps are labelled clearly below so students can follow along.
"""

import time

from fastapi import APIRouter, HTTPException

from app.core.logger import get_logger
from app.schemas.chat import ChatRequest, ChatResponse
from app.services import chroma_service
from app.services.llm_service import generate_response

router = APIRouter()
logger = get_logger()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Send a message and get a RAG-grounded response.

    The user's prompt is first used to search ChromaDB for relevant document
    chunks.  Those chunks are combined with the question before the LLM sees it,
    so the model answers based on YOUR documents — not just its training data.
    """
    llm_name = request.llm.strip().lower()
    started = time.perf_counter()

    logger.info("REQUEST  llm=%s  prompt=%s", llm_name, request.prompt)

    try:
        # ──────────────────────────────────────────────────────────────────────
        # STEP 1 — RETRIEVE
        # Ask ChromaDB: "Which stored text chunks are most similar to the
        # user's question?"  We get back a list of raw text strings.
        # ──────────────────────────────────────────────────────────────────────
        retrieved_context_chunks = chroma_service.retrieve_relevant_chunks(
            user_query=request.prompt,
            number_of_results=3,          # fetch the top 3 most relevant chunks
        )

        logger.info(
            "RETRIEVE chunks_found=%d  prompt=%s",
            len(retrieved_context_chunks),
            request.prompt,
        )

        # ──────────────────────────────────────────────────────────────────────
        # STEP 2 — AUGMENT
        # Combine the retrieved chunks with the user's original question to
        # build a richer prompt.  The model will use the context to ground its
        # answer instead of guessing from training data alone.
        # ──────────────────────────────────────────────────────────────────────
        if retrieved_context_chunks:
            # Join each chunk with a separator so the model can tell them apart.
            retrieved_context = "\n\n---\n\n".join(retrieved_context_chunks)

            # The augmented prompt follows a standard RAG template:
            #   "Here is relevant context.  Now answer this question."
            augmented_prompt = (
                f"Use the following context to answer the question below.\n"
                f"If the context does not contain enough information, say so.\n\n"
                f"Context:\n{retrieved_context}\n\n"
                f"Question: {request.prompt}"
            )
        else:
            # No documents have been uploaded yet — answer the question directly.
            # Students: upload a .txt file via POST /api/upload-document first!
            logger.info("RETRIEVE no chunks found — answering without RAG context")
            augmented_prompt = request.prompt

        # ──────────────────────────────────────────────────────────────────────
        # STEP 3 — GENERATE
        # Pass the augmented prompt (context + question) to the LLM service.
        # The LLM sees richer input and produces a grounded, accurate answer.
        # ──────────────────────────────────────────────────────────────────────
        generated_answer = generate_response(augmented_prompt, request.llm)

    except ValueError as error:
        logger.error("ERROR    llm=%s  %s", llm_name, error)
        raise HTTPException(status_code=400, detail=str(error)) from error

    except Exception as error:
        seconds = time.perf_counter() - started
        logger.exception(
            "ERROR    llm=%s  time=%.2fs  %s: %s",
            llm_name,
            seconds,
            type(error).__name__,
            error,
        )
        raise HTTPException(status_code=500, detail=str(error)) from error

    seconds = time.perf_counter() - started
    logger.info(
        "RESPONSE llm=%s  time=%.2fs  response=%s",
        llm_name,
        seconds,
        generated_answer,
    )

    return ChatResponse(response=generated_answer, llm=llm_name)
