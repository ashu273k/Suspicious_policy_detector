# LexGuard — AI Contract Intelligence

A lightweight contract analysis toolkit that extracts clauses, runs specialized AI agents to detect risks, and generates a concise executive report.

This repository is a full-stack demo with a FastAPI backend and a React + Vite frontend. The project uses Groq for LLM inference, Sentence-Transformers for embeddings, and ChromaDB as a local vector store.

---

## Highlights

- Clause extraction and structured labeling (JSON) from raw contract text
- Multi-agent analysis: liability, privacy, IP, arbitration, and financial checks
- Rate-limit aware Groq client with header-driven throttling and retries
- Paste-or-upload UX: paste contract text or upload PDF/DOCX/TXT
- PDF export of the final analysis report

---

## Quick start (developer)

Prerequisites

- Python 3.10+ (this repo was developed on Python 3.12)
- Node 18+ / npm
- Optional: a Groq API key (recommended for real AI-powered results)

1. Create and activate a virtualenv, then install backend deps:

```bash
python -m venv ./venv
source ./venv/bin/activate
pip install -r backend/requirements.txt
```

2. Copy `.env.example` → `.env` and set your Groq key:

```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY=your_groq_api_key_here
```

3. Start the backend (FastAPI + Uvicorn):

```bash
cd backend
uvicorn main:app --reload --port 8000
```

4. Start the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open the UI at `http://localhost:5173` (Vite default) or the backend at `http://127.0.0.1:8000/docs` for the interactive API docs.

---

## Environment variables

- `GROQ_API_KEY` — Your Groq API key (required for LLM calls)
- `GROQ_MODEL` — Model to use (default: `llama-3.1-8b-instant`). Prefer smaller, faster models to reduce token-per-minute pressure.

See [`.env.example`](.env.example) for defaults.

---

## Paste vs Upload

- The Upload page supports both file upload (`/api/upload`) and pasted text (`/api/upload_text`). After upload the frontend calls `/api/analyze` with `{ "document_id": "..." }`.
- If you get a `400` response with `{"detail":"document_id is required"}`, the upload did not return a valid `document_id`.

---

## Rate limiting & best practices

- The backend uses a Groq HTTP client at `backend/llm/groq_client.py` that reads rate-limit headers like `x-ratelimit-remaining-tokens` and `retry-after` to decide whether to delay or retry calls.
- Default runtime behavior reduces bursts by running clause analysis with `max_workers=1` to avoid hitting RPM/TPM limits.
- Tips to reduce API pressure:
  - Use a smaller model in `GROQ_MODEL` (e.g. `llama-3.1-8b-instant`).
  - Increase `max_tokens` conservatively in `groq_client.py` when you need longer generations.
  - Use batching and cached embeddings where possible.

---

## Troubleshooting

- `422 Unprocessable Entity` on `/api/analyze` — older behavior; after recent fixes the endpoint now returns `400` with a helpful message when `document_id` is missing. Ensure upload succeeded and returned a `document_id`.
- `ModuleNotFoundError: No module named 'sentence_transformers'` — install the Python dependencies in the backend venv: `pip install -r backend/requirements.txt`.
- If the server reports `Address already in use` on start, kill previous uvicorn instances (`pkill -f uvicorn`) and restart.

---

## Development notes

- Primary backend files:
  - `backend/main.py` — FastAPI app bootstrap
  - `backend/api/routes/upload.py` — upload and paste endpoints
  - `backend/api/routes/analyze.py` — analysis orchestration
  - `backend/llm/groq_client.py` — Groq HTTP client with throttling
  - `backend/extraction/clause_extractor.py` — prompt + parsing logic

- Frontend lives in `frontend/` and communicates with the backend via `frontend/src/api/lexguard.js`.

---

## Contributing

Bug reports, suggestions and PRs are welcome. Please open issues for non-trivial proposals.

---

## License

MIT
