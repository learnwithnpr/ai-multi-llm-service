import time

from fastapi import APIRouter, HTTPException

from app.core.logger import get_logger
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import generate_response


router = APIRouter()
logger = get_logger()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    llm = request.llm.strip().lower()
    started = time.perf_counter()

    logger.info("REQUEST  llm=%s  prompt=%s", llm, request.prompt)

    try:
        answer = generate_response(request.prompt, request.llm)
    except ValueError as error:
        logger.error("ERROR    llm=%s  %s", llm, error)
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        seconds = time.perf_counter() - started
        logger.exception(
            "ERROR    llm=%s  time=%.2fs  %s: %s",
            llm,
            seconds,
            type(error).__name__,
            error,
        )
        raise HTTPException(status_code=500, detail=str(error)) from error

    seconds = time.perf_counter() - started
    logger.info(
        "RESPONSE llm=%s  time=%.2fs  response=%s",
        llm,
        seconds,
        answer,
    )
    return ChatResponse(response=answer, llm=llm)
