# Case Analyst - Legal AI Assessment MVP

A working legal AI assessment project for a fictional law-firm scenario. The application accepts one or more legal documents, extracts text, runs a Case Analyst AI Agent, retrieves supporting internal knowledge, invokes the configured LLM, and returns a structured first-pass legal assessment.

> Demo/assessment only. Use only fictional, synthetic, or public material. It is not an official production system and does not provide final legal advice.

## Core assessment workflow

`Upload PDF/DOCX/TXT -> Extract Text -> Case Analyst Agent -> RAG -> Anthropic Claude -> Structured Legal Report -> Web UI`

The `CaseAnalystAgent` is separate from the LLM. It orchestrates retrieval, prompt preparation, model invocation, response validation, and report generation.

## Structured report

- Case Summary
- Strong Points
- Weak Points
- Potential Legal Risks
- Missing Evidence or Information
- Key People, Companies, Organizations, and Dates
- Suggested Questions
- Recommended Next Steps

## Technology choices

- Python + FastAPI for REST APIs and automatic Swagger/OpenAPI documentation
- SQLAlchemy with SQLite for the local MVP; PostgreSQL can be configured
- `pypdf` for PDF text extraction
- `python-docx` for DOCX text extraction
- TF-IDF + cosine similarity for lightweight RAG over the small demo knowledge base
- Anthropic Claude integration through the Messages API
- Ollama + Llama 3.2 retained only as a free local-development fallback

## LLM configuration

Copy the environment file:

```bash
copy .env.example .env
```

### Anthropic Claude (assessment-required provider)

Set:

```env
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

No API key is included in this repository.

### Free local development fallback

If Claude API access is not available, the project can still be tested locally with Ollama:

```env
LLM_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.2:3b
```

Then:

```bash
ollama pull llama3.2:3b
```

The UI always displays the actual provider/model used, so the demo is transparent.

## Run on Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Open:

- Web app: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## Demo case

Use:

`sample_cases/fictional_supply_agreement_dispute.txt`

The sample is fictional and intentionally contains both supporting facts and missing evidence so the Case Analyst can demonstrate strengths, weaknesses, risks, missing information, questions, and next steps.

## Important endpoints

- `POST /cases/analyze` - upload one or more PDF/DOCX/TXT files and generate the structured report
- `GET /cases/recent` - show recent stored analyses
- `GET /health` - health check
- Existing `/matters` endpoints are retained as a secondary workflow from the earlier MVP

## Architecture

See `docs/architecture.svg` and `DESIGN.md`.

## Production improvements

For real legal work, add strong authentication/RBAC, document-level authorization, encryption and secret management, audit logging, malware/file scanning, retention/deletion policies, observability, test coverage, human approval, citations to source passages, prompt/version management, evaluation datasets, PostgreSQL, and an embeddings/vector database for larger document collections.
