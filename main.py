from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chat import router as chat_router


app = FastAPI(
    title="AI Multi LLM API",
    description="Simple FastAPI app that routes a prompt to OpenAI or Groq",
)

# Angular UI runs on port 4200. Without CORS the browser blocks the API.
# allow_private_network is required for Chrome's localhost preflight.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    # allow_private_network=True,
    expose_headers=["*"],
)

app.include_router(chat_router, prefix="/api")


@app.get("/")
def home():
    return {"message": "AI Multi LLM API is running"}
