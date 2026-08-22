from pydantic import BaseModel


class ChatRequest(BaseModel):
    prompt: str
    llm: str  # "openai" or "groq"


class ChatResponse(BaseModel):
    response: str
    llm: str
