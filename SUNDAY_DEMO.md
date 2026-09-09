# Sunday demo - 7 minute plan

1. **Problem (45 sec)** - Lawyers need a faster, consistent first-pass review of case materials. The AI assists; it does not replace legal judgement.
2. **Architecture (60 sec)** - Upload -> extraction -> CaseAnalystAgent -> RAG -> Claude/configured LLM -> structured report -> database/UI.
3. **Agent vs LLM (30 sec)** - The Agent orchestrates the workflow; Claude is the model that generates the analysis.
4. **Live demo (3 min)** - Upload `sample_cases/fictional_supply_agreement_dispute.txt`, click Analyze, then show all required report sections and retrieved knowledge.
5. **Code (60 sec)** - Show `document_processor.py`, `case_agent.py`, `llm.py`, and `rag.py` in that order.
6. **Production improvements (45 sec)** - RBAC, document permissions, encryption, audit logs, vector DB, source citations, evaluation, PostgreSQL.

Important: If the demo uses Ollama because Claude API access is unavailable, say that clearly. Explain that the Claude integration is implemented/configurable and that Ollama is only the local-development fallback.
