from typing import Any

from .llm import generate_structured_analysis
from .rag import retrieve_top_k

REQUIRED_FIELDS = {
    "case_summary": str,
    "strong_points": list,
    "weak_points": list,
    "potential_legal_risks": list,
    "missing_evidence_or_information": list,
    "key_entities_and_dates": list,
    "suggested_questions": list,
    "recommended_next_steps": list,
}


class CaseAnalystAgent:
    """Orchestrates retrieval, prompt construction, LLM invocation and response validation."""

    def __init__(self, top_k: int = 2, retrieval_threshold: float = 0.05):
        self.top_k = top_k
        self.retrieval_threshold = retrieval_threshold

    def _build_prompt(self, case_text: str, retrieved: list[dict[str, Any]]) -> str:
        if retrieved:
            knowledge = "\n\n".join(
                f"SOURCE: {item['name']} (similarity={item['score']:.3f})\n{item['text']}"
                for item in retrieved
            )
        else:
            knowledge = "No sufficiently relevant internal knowledge article was retrieved."

        return f"""
You are Case Analyst, an AI assistant supporting lawyers with a structured first-pass review of a fictional legal case.

IMPORTANT RULES:
- This is decision support, not final legal advice.
- Base your analysis on the uploaded case material.
- Treat the retrieved internal knowledge as supporting context, not as a substitute for the case documents.
- If evidence is missing or uncertain, say so explicitly.
- Do not invent facts, people, dates, obligations, or evidence.
- Return ONLY valid JSON. Do not wrap the JSON in markdown.

UPLOADED CASE MATERIAL:
{case_text}

RETRIEVED INTERNAL KNOWLEDGE:
{knowledge}

Return exactly one JSON object using this schema:
{{
  "case_summary": "A concise first-pass summary of the case",
  "strong_points": ["..."],
  "weak_points": ["..."],
  "potential_legal_risks": ["..."],
  "missing_evidence_or_information": ["..."],
  "key_entities_and_dates": ["Person/Company/Organization/Date - relevance"],
  "suggested_questions": ["Question for lawyer or client"],
  "recommended_next_steps": ["Practical next step"]
}}
""".strip()

    @staticmethod
    def _validate_report(report: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {}
        for field, expected_type in REQUIRED_FIELDS.items():
            value = report.get(field)
            if expected_type is str:
                normalized[field] = str(value or "Not identified from the supplied material.").strip()
            else:
                if value is None:
                    normalized[field] = []
                elif isinstance(value, list):
                    normalized[field] = [str(item).strip() for item in value if str(item).strip()]
                else:
                    normalized[field] = [str(value).strip()]
        return normalized

    def analyze(self, case_text: str) -> dict[str, Any]:
        retrieved = retrieve_top_k(
            case_text,
            top_k=self.top_k,
            minimum_score=self.retrieval_threshold,
        )
        prompt = self._build_prompt(case_text, retrieved)
        report, provider, model = generate_structured_analysis(prompt)
        report = self._validate_report(report)

        return {
            "report": report,
            "llm_provider": provider,
            "llm_model": model,
            "knowledge_sources": [
                {"name": item["name"], "score": round(float(item["score"]), 4)}
                for item in retrieved
            ],
        }
