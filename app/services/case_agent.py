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
    """
    Orchestrates retrieval, prompt construction,
    LLM invocation and response validation.
    """

    def __init__(
        self,
        top_k: int = 2,
        retrieval_threshold: float = 0.05,
    ):
        self.top_k = top_k
        self.retrieval_threshold = retrieval_threshold

    def _build_prompt(
        self,
        case_text: str,
        retrieved: list[dict[str, Any]],
        language: str = "en",
    ) -> str:

        if retrieved:
            knowledge = "\n\n".join(
                (
                    f"SOURCE: {item['name']} "
                    f"(similarity={item['score']:.3f})\n"
                    f"{item['text']}"
                )
                for item in retrieved
            )
        else:
            knowledge = (
                "No sufficiently relevant internal "
                "knowledge article was retrieved."
            )

        requested_language = (
            "Arabic"
            if language.lower() == "ar"
            else "English"
        )

        return f"""
You are Case Analyst, an AI assistant supporting lawyers
with a structured first-pass review of a fictional legal case.

IMPORTANT RULES:
- This is decision support, not final legal advice.
- Base your analysis on the uploaded case material.
- Treat the retrieved internal knowledge as supporting context,
  not as a substitute for the case documents.
- If evidence is missing or uncertain, say so explicitly.
- Do not invent facts, people, dates, obligations, or evidence.
- Return ONLY valid JSON.
- Do not wrap the JSON in markdown.
- Write ALL report values in {requested_language}.
- Keep the JSON field names exactly as defined in the schema below.
- If the requested language is Arabic, use clear Modern Standard
  Arabic suitable for a professional legal audience.
- Proper names may remain in their original language when
  translation would reduce accuracy.

UPLOADED CASE MATERIAL:
{case_text}

RETRIEVED INTERNAL KNOWLEDGE:
{knowledge}

Return exactly one JSON object using this schema:

{{
  "case_summary": "A concise first-pass summary of the case",

  "strong_points": [
    "..."
  ],

  "weak_points": [
    "..."
  ],

  "potential_legal_risks": [
    "..."
  ],

  "missing_evidence_or_information": [
    "..."
  ],

  "key_entities_and_dates": [
    "Return ONLY plain text strings, never objects or dictionaries. Example: Ahmed Hassan — Gulf Horizon Technologies LLC — 1 January 2025"
  ],

  "suggested_questions": [
    "Question for lawyer or client"
  ],

  "recommended_next_steps": [
    "Practical next step"
  ]
}}
""".strip()

    @staticmethod
    def _validate_report(
        report: dict[str, Any]
    ) -> dict[str, Any]:

        normalized: dict[str, Any] = {}

        for field, expected_type in REQUIRED_FIELDS.items():

            value = report.get(field)

            if expected_type is str:

                normalized[field] = str(
                    value
                    or "Not identified from the supplied material."
                ).strip()

            else:

                if value is None:

                    normalized[field] = []

                elif isinstance(value, list):

                    normalized[field] = [
                        str(item).strip()
                        for item in value
                        if str(item).strip()
                    ]

                else:

                    normalized[field] = [
                        str(value).strip()
                    ]

        return normalized

    def analyze(
        self,
        case_text: str,
        language: str = "en",
        ai_mode: str = "claude",
    ) -> dict[str, Any]:

        # ---------------------------------------------
        # LANGUAGE
        # ---------------------------------------------

        language = (
            "ar"
            if str(language).lower() == "ar"
            else "en"
        )

        # ---------------------------------------------
        # AI MODE
        # ---------------------------------------------

        ai_mode = str(ai_mode).lower().strip()

        allowed_modes = {
            "claude",
            "hosted",
        }

        if ai_mode not in allowed_modes:
            ai_mode = "claude"

        # Note:
        # Offline mode is handled in main.py before
        # this Agent is called.
        #
        # Therefore the Agent only receives:
        #
        # claude
        # hosted

        # ---------------------------------------------
        # RAG RETRIEVAL
        # ---------------------------------------------

        retrieved = retrieve_top_k(
            case_text,
            top_k=self.top_k,
            minimum_score=self.retrieval_threshold,
        )

        # ---------------------------------------------
        # BUILD AGENT PROMPT
        # ---------------------------------------------

        prompt = self._build_prompt(
            case_text,
            retrieved,
            language=language,
        )

        # ---------------------------------------------
        # DYNAMIC LLM PROVIDER
        # ---------------------------------------------

        report, provider, model = (
            generate_structured_analysis(
                prompt,
                provider=ai_mode,
            )
        )

        # ---------------------------------------------
        # VALIDATE STRUCTURED RESULT
        # ---------------------------------------------

        report = self._validate_report(
            report
        )

        # ---------------------------------------------
        # RETURN RESULT
        # ---------------------------------------------

        return {
            "report": report,

            "llm_provider": provider,

            "llm_model": model,

            "language": language,

            "ai_mode": ai_mode,

            "knowledge_sources": [
                {
                    "name": item["name"],
                    "score": round(
                        float(item["score"]),
                        4,
                    ),
                }
                for item in retrieved
            ],
        }