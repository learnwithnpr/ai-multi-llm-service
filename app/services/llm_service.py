from app.core.logger import get_logger
from app.services import groq_service, openai_service

logger = get_logger()


def generate_response(prompt: str, llm: str) -> str:
    # Students: this is the only new idea.
    # The API body says which provider to use.
    name = llm.strip().lower()

    if name == "openai":
        logger.info("CALL     provider=openai")
        return openai_service.generate_response(prompt)

    if name == "groq":
        logger.info("CALL     provider=groq")
        return groq_service.generate_response(prompt)

    raise ValueError("llm must be 'openai' or 'groq'")
