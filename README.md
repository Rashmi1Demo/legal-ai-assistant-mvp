# AlGhazzawi Legal AI Assistant - Demo MVP

A small working AI-enabled law firm operations MVP prepared for technical demonstration purposes.

> **Important:** This is a demo/assessment project. It is not an official AlGhazzawi production system and does not contain confidential company or client data.

## What It Demonstrates

- FastAPI REST APIs
- Legal matter / service request intake
- AI-assisted practice-area classification
- Priority recommendation
- RAG-style retrieval from an internal legal knowledge base
- Local LLM integration using Ollama + Llama 3.2
- AI-generated matter summary and suggested next step
- Matter lifecycle and status updates
- Dashboard for legal matters
- SQLAlchemy database integration
- SQLite by default; PostgreSQL supported
- Swagger API documentation
- Application architecture

## Technology Stack

- **Backend:** Python, FastAPI
- **AI/LLM:** Ollama, Llama 3.2
- **Retrieval:** TF-IDF and cosine similarity
- **Database:** SQLAlchemy, SQLite / PostgreSQL
- **API:** REST APIs
- **API Documentation:** Swagger / OpenAPI
- **Frontend:** HTML, CSS and JavaScript

## Example Use Case

**Client / Matter Name:**

`Al Noor Trading Company`

**Title:**

`Review termination clause in supply agreement`

**Description:**

`The client wants to review the termination clause in a supply agreement and understand the notice requirements and key obligations before taking further action.`

**Expected AI Output:**

- Practice Area: Contract Review
- Priority: Medium
- Relevant internal knowledge source
- AI-generated matter summary
- Suggested next step

## AI Workflow

The application follows this workflow:

```text
Legal Matter
     |
     v
FastAPI API
     |
     v
Practice Area & Priority Classification
     |
     v
RAG-Style Knowledge Retrieval
     |
     v
Internal Legal Knowledge Base
     |
     v
Ollama / Llama 3.2
     |
     v
AI Summary + Suggested Next Step
     |
     v
Database
     |
     v
Matter Dashboard
```

## Architecture

```text
User
  |
  v
Legal AI Web Portal
  |
  v
FastAPI REST API
  |
  +--------------------> SQLAlchemy / Database
  |
  +--------------------> Practice Area & Priority Classification
  |
  +--------------------> RAG Retriever
  |                         |
  |                         v
  |                  Internal Legal Knowledge Base
  |                         |
  |                         v
  +--------------------> Ollama / Llama 3.2
                            |
                            v
                 AI Summary + Suggested Next Step
```

## How the Application Works

1. The user submits a legal matter through the web interface.
2. FastAPI receives and validates the request.
3. The application identifies the relevant practice area and recommends a priority.
4. The retrieval layer searches the internal legal knowledge base using TF-IDF and cosine similarity.
5. Relevant knowledge is provided as context to the locally hosted Llama 3.2 model through Ollama.
6. The LLM generates a concise matter summary and suggested next step.
7. The legal matter and AI-generated results are stored using SQLAlchemy.
8. The matter appears in the dashboard where its status can be managed.

## Run the Project

### 1. Create a virtual environment

```bash
python -m venv venv
```

### 2. Activate the virtual environment

Windows Command Prompt:

```bash
venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the environment configuration

```bash
copy .env.example .env
```

### 5. Install Ollama and download the model

Make sure Ollama is installed.

Then run:

```bash
ollama pull llama3.2:3b
```

You can confirm the model with:

```bash
ollama list
```

### 6. Start the FastAPI application

```bash
uvicorn app.main:app --reload
```

### 7. Open the application

Application:

`http://127.0.0.1:8000`

Swagger API documentation:

`http://127.0.0.1:8000/docs`

## Database Integration

The MVP uses **SQLAlchemy ORM** for database integration.

SQLite is used by default to keep the demo simple and easy to run.

The application stores legal matter information including:

- Client / matter name
- Request title
- Description
- Practice area
- Priority
- AI-generated summary
- Suggested next step
- Knowledge source
- Matter status

## PostgreSQL Support

For PostgreSQL, update `DATABASE_URL` in the `.env` file:

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/legal_ai
```

## API Documentation

FastAPI automatically provides Swagger/OpenAPI documentation.

After starting the application, open:

`http://127.0.0.1:8000/docs`

The API can be tested directly from the Swagger interface.

## Knowledge Retrieval

For this MVP, the retrieval layer uses **TF-IDF and cosine similarity** to identify relevant information from the internal legal knowledge base.

This provides a lightweight RAG-style implementation suitable for demonstrating the complete AI workflow without requiring an external vector database.

For a production implementation, the retrieval layer could be extended with embeddings and a vector database depending on scale and requirements.

## Local LLM

The MVP uses **Llama 3.2 through Ollama**.

The LLM runs locally and is used to generate:

- Matter summaries
- Suggested next steps

The LLM integration can later be replaced or extended with other model providers depending on production requirements.

## Project Structure

```text
app/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── services/
│   ├── ai.py
│   └── rag.py
└── static/
    └── index.html

knowledge_base/
docs/
README.md
requirements.txt
.env.example
```

## Disclaimer

This application was created as a technical demonstration MVP. The legal knowledge included in the project is sample content only and should not be treated as legal advice.
