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
        # Teaching: uncomment one idea at a time.
        # instructions="You are a teacher. Use simple words. Answer in 2 sentences.",
        # temperature=0.2,       # 0 = focused / same answer. 1 = more creative. Range 0 to 2.
        # top_p=0.9,             # nucleus sampling. Use this OR temperature, not both at first.
        # max_output_tokens=50,  # stop after ~50 tokens. Good length + cost demo.
        # top_k is not supported on OpenAI. Use it in groq_service.py.
    )

    return response.output_text


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Convert a list of text strings into a list of embeddings (lists of floats)."""
    api_key = get_openai_api_key()
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing. Put it in the .env file.")

    client = OpenAI(api_key=api_key)

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )

    return [item.embedding for item in response.data]


def get_embedding(text: str) -> list[float]:
    """Convert a single text string into an embedding."""
    return get_embeddings([text])[0]
