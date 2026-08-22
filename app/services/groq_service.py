from openai import OpenAI

from app.core.config import get_groq_api_key

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "openai/gpt-oss-20b"


def generate_response(prompt: str) -> str:
    api_key = get_groq_api_key()
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing. Put it in the .env file.")

    client = OpenAI(
        api_key=api_key,
        base_url=GROQ_BASE_URL,
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content
