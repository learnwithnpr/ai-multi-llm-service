import os
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


def load_keys() -> None:
    # Re-read .env every request so a new key works after you save .env.
    # uvicorn --reload does not watch .env files.
    load_dotenv(dotenv_path=ENV_FILE, override=True)


def get_openai_api_key() -> str | None:
    load_keys()
    return os.getenv("OPENAI_API_KEY")


def get_groq_api_key() -> str | None:
    load_keys()
    return os.getenv("GROQ_API_KEY")
