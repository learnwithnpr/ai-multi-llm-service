# AI Multi LLM Service

FastAPI app that sends a **single prompt** to **OpenAI** or **Groq**.

There is **no chat memory**. Each request is a new question. Use this class first. The next class is `ai-chat-history-service`.

## API

`POST /api/chat`

```json
{
  "prompt": "My name is Raju",
  "llm": "groq"
}
```

Reply:

```json
{
  "response": "...",
  "llm": "groq"
}
```

`llm` must be `openai` or `groq`.

## Class demo (no history)

1. Ask: `My name is Raju`
2. Ask: `What is my name?`
3. The model should **not** know, because this API only sends the new prompt.

Then switch to `ai-chat-history-service` on port **8003**.

## Folders

```
ai-multi-llm-service/
├── main.py                         start FastAPI + CORS
├── requirements.txt
├── .env.example
├── logs/app.log                    created at runtime
└── app/
    ├── core/config.py              reads API keys from .env
    ├── core/logger.py              console + file logger
    ├── schemas/chat.py             prompt + llm
    ├── services/openai_service.py
    ├── services/groq_service.py
    ├── services/llm_service.py     if/else router
    └── routes/chat.py              POST /api/chat
```

## Run

### Mac / Linux

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

### Windows (Command Prompt)

```bat
cd ai-multi-llm-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Put both keys in `.env`, then:

```bat
.venv\Scripts\uvicorn main:app --reload --port 8002
```

Docs: http://localhost:8002/docs

## Teaching flags

These settings are commented out in the service files. Uncomment **one idea at a time**.

| Setting | File | What it does | Try |
|---------|------|--------------|-----|
| `temperature` | both | How random the answer is | `0.0` then `1.2` |
| `top_p` | both | Keep tokens that add up to probability `p` | `0.2` then `0.95` |
| `top_k` | Groq only | Keep the `k` most likely next tokens | `10` then `40` |
| `max_output_tokens` | OpenAI | Stop after this many tokens | `20` then `200` |
| `max_tokens` | Groq | Same idea | `20` then `200` |
| `instructions` | OpenAI | System style rules | "Answer in 2 sentences." |
| `seed` | Groq | Same seed + low temperature ≈ same answer | `42` |
