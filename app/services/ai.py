import os
import requests
from dotenv import load_dotenv
from .rag import retrieve

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

def classify_matter(text: str):
    lower = text.lower()

    if any(k in lower for k in ["termination clause", "contract", "agreement", "nda", "review clause"]):
        practice_area = "Contract Review"
    elif any(k in lower for k in ["employee", "employment", "termination procedure", "hr", "labor"]):
        practice_area = "Employment"
    elif any(k in lower for k in ["litigation", "court", "claim", "dispute", "hearing"]):
        practice_area = "Dispute Resolution"
    elif any(k in lower for k in ["corporate", "company formation", "shareholder", "board", "m&a"]):
        practice_area = "Corporate"
    elif any(k in lower for k in ["compliance", "policy", "regulatory", "privacy", "data protection"]):
        practice_area = "Compliance"
    else:
        practice_area = "General Legal"

    if any(k in lower for k in ["urgent", "today", "hearing tomorrow", "deadline today", "critical"]):
        priority = "High"
    elif any(k in lower for k in ["termination", "deadline", "client waiting", "time sensitive"]):
        priority = "Medium"
    else:
        priority = "Normal"

    return practice_area, priority

def call_ollama(prompt: str):
    response = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=120
    )
    response.raise_for_status()
    return response.json()["response"].strip()

def analyze_matter(title: str, description: str, client_name: str | None = None):
    full_text = f"{title}. {description}"
    practice_area, priority = classify_matter(full_text)
    kb = retrieve(full_text)

    prompt = f"""
You are an internal legal operations assistant for a law firm.

This is a demo workflow. Do not give definitive legal advice.
Use only the internal knowledge provided below to summarize the request and suggest the next operational step.

Client:
{client_name or "Not specified"}

Request Title:
{title}

Request Description:
{description}

Recommended Practice Area:
{practice_area}

Recommended Priority:
{priority}

Relevant Internal Knowledge:
{kb['text']}

Return exactly:

SUMMARY:
<one concise sentence>

NEXT STEP:
<short operational suggestion grounded in the internal knowledge>
"""

    try:
        llm_response = call_ollama(prompt)

        if "SUMMARY:" in llm_response and "NEXT STEP:" in llm_response:
            parts = llm_response.split("NEXT STEP:", 1)
            summary = parts[0].replace("SUMMARY:", "").strip()
            next_step = parts[1].strip()
        else:
            summary = f"{practice_area} request: {title}"
            next_step = llm_response

    except Exception as exc:
        print("Ollama error:", exc)
        summary = f"{practice_area} request: {title}"
        next_step = f"Local LLM unavailable. Review internal knowledge article: {kb['name']}."

    return {
        "practice_area": practice_area,
        "priority": priority,
        "ai_summary": summary,
        "suggested_next_step": next_step,
        "knowledge_source": kb["name"]
    }
