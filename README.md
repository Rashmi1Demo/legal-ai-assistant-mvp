# AlGhazzawi Legal AI Assistant - Demo MVP

A small working AI-enabled law firm operations MVP prepared for technical demonstration purposes.

> Important: This is a demo/assessment project. It is not an official AlGhazzawi production system and does not contain confidential company or client data.

## What it demonstrates

- FastAPI REST APIs
- Legal matter / service request intake
- AI-assisted practice-area classification
- Priority recommendation
- RAG-style retrieval from an internal legal knowledge base
- Local LLM through Ollama + Llama 3.2
- AI-generated matter summary and next-step suggestion
- Matter lifecycle status updates
- Dashboard
- SQLite by default; PostgreSQL supported
- Swagger API documentation
- Architecture diagram

## Example use case

Title:
`Review termination clause in Client ABC contract`

Description:
`Client wants to know the notice period and key points to review before termination.`

Expected:
- Practice Area: Contract Review
- Priority: Medium
- Knowledge Source: contract_termination_review
- AI Summary
- Suggested Next Step

## Run

Windows:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Make sure Ollama is installed and the model exists:

```bash
ollama pull llama3.2:3b
```

Open:

- App: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

## Architecture

User -> Legal AI Web Portal -> FastAPI -> Database
                                      |
                                      +-> Classification
                                      |
                                      +-> RAG Retriever -> Internal Knowledge Base
                                                           |
                                                           +-> Ollama / Llama 3.2
                                                                    |
                                                                    -> AI Summary + Suggested Next Step

## PostgreSQL

Set in `.env`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/legal_ai
```
