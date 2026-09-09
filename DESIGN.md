# Case Analyst - Short Design Document

## 1. Business problem and solution

Lawyers often need to spend time reading new case materials before they can identify the basic facts, strengths, weaknesses, risks, missing evidence, and next actions. The Case Analyst MVP demonstrates how an AI assistant can create a consistent first-pass assessment while keeping the lawyer responsible for final professional judgement.

A user uploads one or more fictional legal documents in PDF, DOCX, or TXT format. The application extracts their text automatically and passes the combined case material to a Case Analyst Agent. The Agent retrieves relevant supporting knowledge, prepares a controlled prompt, invokes the configured LLM, validates the returned structure, stores the result, and displays a structured report in the browser.

## 2. Architecture and technology choices

FastAPI is used because it is lightweight, works well with Python AI services, provides request validation, and automatically exposes Swagger/OpenAPI documentation. SQLAlchemy provides database abstraction; SQLite keeps the MVP easy to run locally, while PostgreSQL can be configured for a larger implementation.

Document processing is intentionally simple and local. TXT is decoded directly, DOCX is parsed with `python-docx`, and text-based PDF files are parsed with `pypdf`. Image-only/scanned PDFs are reported as unsupported rather than silently producing a poor analysis. OCR could be added later.

For the small demo knowledge base, RAG uses TF-IDF and cosine similarity. This is easy to inspect and explain and avoids adding unnecessary infrastructure. For a production corpus containing many legal documents, embeddings plus a vector store such as pgvector would provide stronger semantic retrieval and metadata filtering.

## 3. AI Agent design and prompt strategy

The `CaseAnalystAgent` is an orchestration component, not the LLM itself. Its responsibilities are:

1. Receive extracted case text.
2. Retrieve the most relevant internal knowledge items.
3. Build a controlled legal-analysis prompt.
4. Invoke the configured LLM provider.
5. Parse and validate the structured JSON response.
6. Return the report together with provider/model and retrieval metadata.

The prompt tells the model that the output is decision support rather than final legal advice, requires it to use the uploaded material, instructs it not to invent missing facts, and requires a fixed JSON schema. A low temperature is used for Claude to encourage consistency.

The required output contains Case Summary, Strong Points, Weak Points, Potential Legal Risks, Missing Evidence or Information, Key Entities and Dates, Suggested Questions, and Recommended Next Steps.

Anthropic Claude is implemented through the Messages API. The API key is never hard-coded. For zero-cost local development, Ollama can be configured as a fallback; the application reports the actual provider/model used so this is not hidden during a demonstration.

## 4. Assumptions, limitations, and security

The assessment uses only fictional, synthetic, or public documents. The MVP is not suitable for confidential client data as-is. Before real deployment, the system would require authentication, role-based and document-level authorization, encryption in transit/at rest, audit trails, secret management, malware scanning, retention controls, environment isolation, and review of the LLM provider's contractual/data-handling terms.

The current PDF parser extracts embedded text only and does not perform OCR. Long documents are not yet chunked by token limits before LLM analysis. The current RAG knowledge base is very small. AI output can still be incomplete or incorrect, so a lawyer must review all generated analysis.

## 5. Future improvements

A production version would add document chunking, embeddings/vector retrieval, source citations, confidence/evidence indicators, Arabic support, PDF report export, stronger evaluation tests, prompt/version tracking, model monitoring, background processing for large files, PostgreSQL, and enterprise identity integration. A human approval step would be retained before any legal conclusion or client-facing action.
