# 3-Minute Demo Script

"This is a small AI-powered law firm operations MVP. It demonstrates matter intake, AI-assisted classification, knowledge retrieval, and a locally hosted LLM using Ollama."

## Demo 1 - Contract Review

Title:
Review termination clause in Client ABC contract

Description:
Client wants to know the notice period and key points to review before termination.

Explain:
"The system classifies the request, recommends priority, retrieves the most relevant internal legal knowledge article, and sends that context to the local LLM."

Show:
- Practice Area
- Priority
- Knowledge Source
- AI Summary
- Suggested Next Step

## Demo 2 - Employment

Title:
Employee termination procedure

Description:
HR needs the internal checklist before starting an employee termination process.

## API Demo

Open `/docs` and show:
- POST /matters
- GET /matters
- GET /matters/{id}
- PATCH /matters/{id}/status
- GET /dashboard

## Architecture

Open `docs/architecture.svg`.

Say:
"The model runs locally for the MVP, so internal content is not sent to an external API. In production, the LLM provider can be replaced with Azure OpenAI or another approved enterprise service."
