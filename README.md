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
cd ai-multi-llm-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
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
