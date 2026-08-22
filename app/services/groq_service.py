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
        messages=[
            # {"role": "system", "content": "You are a teacher. Use simple words. Answer in 2 sentences."},
            {"role": "user", "content": prompt},
        ],
        # Teaching: uncomment one idea at a time.
        # temperature=0.2,        # 0 = focused / same answer. 1 = more creative. Range 0 to 2.
        # top_p=0.9,              # nucleus sampling. Keep only tokens that add up to 90% probability.
        # top_k=40,               # keep only the 40 most likely next tokens. Groq supports this.
        # max_tokens=50,          # stop after ~50 tokens. Good length + cost demo.
        # seed=42,                # same seed + low temperature ≈ same answer again.
        # stop=["END"],           # model stops if it writes this text.
        # frequency_penalty=0.5,  # less repetition of the same words.
    )

    return response.choices[0].message.content
