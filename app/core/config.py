import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


def load_keys() -> None:
    # Re-read .env every request so a new key works after you save .env.
    # uvicorn --reload does not watch .env files.
    load_dotenv(dotenv_path=ENV_FILE, override=True)


# ── Individual helpers (kept for backward-compatibility) ─────────────────────

def get_openai_api_key() -> str:
    load_keys()
    return os.getenv("OPENAI_API_KEY", "")


def get_groq_api_key() -> str:
    load_keys()
    return os.getenv("GROQ_API_KEY", "")


# ── Settings dataclass (new — used by the RAG services) ──────────────────────

@dataclass
class Settings:
    """One place to read all configuration values.

    Students: add a new config value here instead of calling
    os.getenv() scattered across the codebase.
    """
    OPENAI_API_KEY: str
    CHROMA_HOST: str
    CHROMA_PORT: int


def get_settings() -> Settings:
    """Load .env and return a filled-in Settings object."""
    load_keys()
    return Settings(
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
        CHROMA_HOST=os.getenv("CHROMA_HOST", "localhost"),
        CHROMA_PORT=int(os.getenv("CHROMA_PORT", "8000")),
    )
