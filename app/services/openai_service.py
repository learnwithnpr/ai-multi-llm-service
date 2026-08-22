from openai import OpenAI

from app.core.config import get_openai_api_key


def generate_response(prompt: str) -> str:
    api_key = get_openai_api_key()
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing. Put it in the .env file.")

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
    )

    return response.output_text
