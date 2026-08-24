# AI Multi LLM Service

FastAPI app that sends a prompt to **OpenAI** or **Groq**.

Pick the provider with `llm` in the request body.

## API

`POST /api/chat`

```json
{
  "prompt": "Explain FastAPI in simple words",
  "llm": "openai"
}
```

or

```json
{
  "prompt": "Explain FastAPI in simple words",
  "llm": "groq"
}
```

Reply:

```json
{
  "response": "...",
  "llm": "openai"
}
```

`llm` must be `openai` or `groq`. Anything else returns HTTP 400.

## Folders

```
ai-multi-llm-service/
├── main.py                         start FastAPI + CORS
├── requirements.txt
├── .env.example                    copy to .env and add both keys
├── logs/app.log                    created at runtime
└── app/
    ├── core/config.py              reads API keys from .env
    ├── core/logger.py              console + file logger
    ├── schemas/chat.py             prompt + llm
    ├── services/openai_service.py  OpenAI call
    ├── services/groq_service.py    Groq call
    ├── services/llm_service.py     if/else router
    └── routes/chat.py              POST /api/chat
```

## Run

```bash
Step	Windows CMD	Windows PowerShell	Mac/Linux
Enter project	cd ai-multi-llm-service	same	same
Create venv	python -m venv .venv	python -m venv .venv	python3 -m venv .venv
Activate	.venv\Scripts\activate	.venv\Scripts\Activate.ps1	source .venv/bin/activate
Install	pip install -r requirements.txt	same	same
Create .env	copy .env.example .env	Copy-Item .env.example .env	cp .env.example .env
```

Put both keys in `.env`:

```
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
```

```bash
.venv/bin/uvicorn main:app --reload --port 8002
```

Docs: http://localhost:8002/docs

## Logs

Each chat is printed in the terminal and written to `logs/app.log`:

```
2026-08-22 16:30:01 | INFO | REQUEST  llm=groq  prompt=Explain FastAPI
2026-08-22 16:30:01 | INFO | CALL     provider=groq
2026-08-22 16:30:02 | INFO | RESPONSE llm=groq  time=1.12s  response=FastAPI is...
```

Watch the file live:

```bash
tail -f logs/app.log
```

## Teaching flags

These settings are commented out in the service files. Uncomment **one idea at a time**, send the same prompt, and compare answers.

### 1. How random is the next word?

| Setting | File | What it does | Try |
|---------|------|--------------|-----|
| `temperature` | both | How random the answer is | `0.0` then `1.2` |
| `top_p` | both | Keep only tokens that add up to probability `p` | `0.2` then `0.95` |
| `top_k` | Groq only | Keep only the `k` most likely next tokens | `10` then `40` |

OpenAI does **not** support `top_k`. Groq does.

Start with **temperature only**. Do not turn temperature, `top_p`, and `top_k` up together — the result is hard to explain.

### 2. How long is the answer? (also about cost)

| Setting | File | What it does | Try |
|---------|------|--------------|-----|
| `max_output_tokens` | OpenAI | Stop after this many tokens | `20` then `200` |
| `max_tokens` | Groq | Same idea | `20` then `200` |

Same prompt, short cap vs long cap. Students see why APIs charge per token.

### 3. How should the model behave?

| Setting | File | What it does | Try |
|---------|------|--------------|-----|
| `instructions` | OpenAI | System style rules | "Answer in 2 sentences." |
| `messages` `role=system` | Groq | Same idea | Uncomment the system line |

Same user prompt, different system text. That is how chat apps set a persona.

### 4. Extra Groq flags (nice live demos)

| Setting | What it does | Try |
|---------|--------------|-----|
| `seed` | Same seed + low temperature ≈ same answer again | `42` with `temperature=0` |
| `stop` | Stop if the model writes this text | `["END"]` |
| `frequency_penalty` | Less repetition | `0.0` then `0.8` |

### Class demo

1. Open `app/services/openai_service.py` or `app/services/groq_service.py`.
2. Uncomment `temperature=0.0`. Call `/api/chat` twice. Answers stay close.
3. Change to `temperature=1.2`. Answers vary more.
4. Switch to `max_tokens=20` (Groq) or `max_output_tokens=20` (OpenAI). The answer is cut short.
5. Uncomment the system / `instructions` line. Tone changes, prompt stays the same.
6. On Groq, try `top_k=10` and `seed=42`.

### Save for a later class

These are important, but they need more code than one uncommented line:

- **streaming** — tokens arrive one by one (`stream=True`)
- **JSON mode** — force `{ ... }` for APIs
- **tools / function calling** — the model picks a function to run

