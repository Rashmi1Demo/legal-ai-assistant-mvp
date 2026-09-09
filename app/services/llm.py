import json
import os
import re
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()


ANTHROPIC_API_KEY = os.getenv(
    "ANTHROPIC_API_KEY",
    ""
).strip()

ANTHROPIC_MODEL = os.getenv(
    "ANTHROPIC_MODEL",
    "claude-sonnet-4-20250514"
).strip()

ANTHROPIC_URL = os.getenv(
    "ANTHROPIC_URL",
    "https://api.anthropic.com/v1/messages"
).strip()

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
).strip()

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:3b"
).strip()

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "auto"
).strip().lower()


class LLMError(RuntimeError):
    pass


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE
        )
        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned
        )

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError:
        match = re.search(
            r"\{.*\}",
            cleaned,
            flags=re.DOTALL
        )

        if not match:
            raise LLMError(
                "The LLM did not return valid JSON."
            )

        try:
            return json.loads(
                match.group(0)
            )

        except json.JSONDecodeError as exc:
            raise LLMError(
                "The LLM response contained invalid JSON."
            ) from exc


def _call_claude(
    prompt: str
) -> tuple[dict[str, Any], str, str]:

    if not ANTHROPIC_API_KEY:
        raise LLMError(
            "ANTHROPIC_API_KEY is not configured."
        )

    response = requests.post(
        ANTHROPIC_URL,
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": ANTHROPIC_MODEL,
            "max_tokens": 4000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        },
        timeout=180,
    )

    response.raise_for_status()

    payload = response.json()

    content_blocks = payload.get("content") or []

    text = "\n".join(
        block.get("text", "")
        for block in content_blocks
        if block.get("type") == "text"
    )

    # Temporary debugging
    #print("CLAUDE RAW RESPONSE:")
    #print(text)

    return (
        _extract_json(text),
        "Anthropic Claude",
        ANTHROPIC_MODEL
    )


def _call_ollama(
    prompt: str
) -> tuple[dict[str, Any], str, str]:

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "keep_alive": "10m",
            "options": {
                "temperature": 0.1,
                "num_predict": 600,
                "num_ctx": 4096,
            },
        },
        timeout=120,
    )

    response.raise_for_status()

    text = response.json().get(
        "response",
        ""
    ).strip()

    return (
        _extract_json(text),
        "Ollama (local development fallback)",
        OLLAMA_MODEL
    )


def generate_structured_analysis(
    prompt: str
) -> tuple[dict[str, Any], str, str]:

    if LLM_PROVIDER == "claude":
        return _call_claude(prompt)

    if LLM_PROVIDER == "ollama":
        return _call_ollama(prompt)

    if LLM_PROVIDER != "auto":
        raise LLMError(
            "LLM_PROVIDER must be "
            "'auto', 'claude', or 'ollama'."
        )

    if ANTHROPIC_API_KEY:
        try:
            return _call_claude(prompt)

        except Exception as claude_exc:
            try:
                return _call_ollama(prompt)

            except Exception as ollama_exc:
                raise LLMError(
                    f"Claude failed ({claude_exc}); "
                    f"Ollama fallback failed ({ollama_exc})."
                ) from ollama_exc

    return _call_ollama(prompt)