import json
import os
import re
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()


# ------------------------------------------------------
# Anthropic Claude configuration
# ------------------------------------------------------

ANTHROPIC_API_KEY = os.getenv(
    "ANTHROPIC_API_KEY",
    ""
).strip()

ANTHROPIC_MODEL = os.getenv(
    "ANTHROPIC_MODEL",
    "claude-sonnet-5"
).strip()

ANTHROPIC_URL = os.getenv(
    "ANTHROPIC_URL",
    "https://api.anthropic.com/v1/messages"
).strip()


# ------------------------------------------------------
# Ollama configuration
# ------------------------------------------------------

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
).strip()

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:3b"
).strip()


# ------------------------------------------------------
# Hosted LLM / Groq configuration
# ------------------------------------------------------

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    ""
).strip()

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
).strip()

GROQ_URL = os.getenv(
    "GROQ_URL",
    "https://api.groq.com/openai/v1/chat/completions"
).strip()


# ------------------------------------------------------
# Default provider
# ------------------------------------------------------

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "auto"
).strip().lower()


# ------------------------------------------------------
# Custom exception
# ------------------------------------------------------

class LLMError(RuntimeError):
    pass


# ------------------------------------------------------
# JSON extraction
# ------------------------------------------------------

def _extract_json(
    text: str
) -> dict[str, Any]:

    cleaned = text.strip()

    # Remove markdown code fences if returned
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

    # First try direct JSON
    try:
        return json.loads(cleaned)

    except json.JSONDecodeError:
        pass

    # Try extracting JSON object from surrounding text
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


# ------------------------------------------------------
# Anthropic Claude
# ------------------------------------------------------

def _call_claude(
    prompt: str
) -> tuple[dict[str, Any], str, str]:

    if not ANTHROPIC_API_KEY:
        raise LLMError(
            "ANTHROPIC_API_KEY is not configured."
        )

    try:

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
                        "content": prompt,
                    }
                ],
            },
            timeout=180,
        )

        response.raise_for_status()

    except requests.RequestException as exc:

        error_message = str(exc)

        # Try to include Anthropic response details
        try:
            if response is not None:
                error_message += (
                    f" | Response: {response.text}"
                )
        except Exception:
            pass

        raise LLMError(
            f"Claude API request failed: {error_message}"
        ) from exc

    try:
        payload = response.json()

    except ValueError as exc:
        raise LLMError(
            "Claude returned a non-JSON API response."
        ) from exc

    # --------------------------------------------------
    # Claude can return multiple content blocks.
    #
    # Example:
    # content = [
    #     {"type": "thinking", ...},
    #     {"type": "text", "text": "..."}
    # ]
    #
    # Therefore do NOT assume content[0]["text"].
    # --------------------------------------------------

    content_blocks = payload.get(
        "content",
        []
    )

    if not isinstance(
        content_blocks,
        list
    ):
        raise LLMError(
            "Claude returned an unexpected content format."
        )

    text_parts = []

    for block in content_blocks:

        if not isinstance(
            block,
            dict
        ):
            continue

        if (
            block.get("type") == "text"
            and isinstance(
                block.get("text"),
                str
            )
        ):

            text_parts.append(
                block["text"]
            )

    text = "\n".join(
        text_parts
    ).strip()

    if not text:

        raise LLMError(
            "Claude response did not contain a text block."
        )

    return (
        _extract_json(text),
        "Anthropic Claude",
        ANTHROPIC_MODEL,
    )


# ------------------------------------------------------
# Ollama local LLM
# ------------------------------------------------------

def _call_ollama(
    prompt: str
) -> tuple[dict[str, Any], str, str]:

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.1,
                    "num_predict": 600,
                    "num_ctx": 4096,
                },
            },
            timeout=180,
        )

        response.raise_for_status()

    except requests.RequestException as exc:

        raise LLMError(
            f"Ollama request failed: {exc}"
        ) from exc

    try:
        payload = response.json()

    except ValueError as exc:
        raise LLMError(
            "Ollama returned a non-JSON API response."
        ) from exc

    text = payload.get(
        "response",
        ""
    )

    if not isinstance(
        text,
        str
    ) or not text.strip():

        raise LLMError(
            "Ollama returned an empty response."
        )

    return (
        _extract_json(text),
        "Ollama (Local LLM)",
        OLLAMA_MODEL,
    )


# ------------------------------------------------------
# Hosted LLM / Groq
# ------------------------------------------------------

def _call_hosted_llm(
    prompt: str
) -> tuple[dict[str, Any], str, str]:

    if not GROQ_API_KEY:

        raise LLMError(
            "GROQ_API_KEY is not configured."
        )

    try:

        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization":
                    f"Bearer {GROQ_API_KEY}",
                "Content-Type":
                    "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "temperature": 0.1,
            },
            timeout=180,
        )

        response.raise_for_status()

    except requests.RequestException as exc:

        error_message = str(exc)

        try:
            if response is not None:
                error_message += (
                    f" | Response: {response.text}"
                )
        except Exception:
            pass

        raise LLMError(
            f"Hosted LLM request failed: {error_message}"
        ) from exc

    try:

        payload = response.json()

    except ValueError as exc:

        raise LLMError(
            "Hosted LLM returned a non-JSON API response."
        ) from exc

    try:

        text = (
            payload["choices"][0]
            ["message"]["content"]
        )

    except (
        KeyError,
        IndexError,
        TypeError
    ) as exc:

        raise LLMError(
            "Hosted LLM returned an unexpected response."
        ) from exc

    if not isinstance(
        text,
        str
    ) or not text.strip():

        raise LLMError(
            "Hosted LLM returned an empty response."
        )

    return (
        _extract_json(text),
        "Hosted LLM (Groq)",
        GROQ_MODEL,
    )


# ------------------------------------------------------
# Main provider selector
# ------------------------------------------------------

def generate_structured_analysis(
    prompt: str,
    provider: str | None = None,
) -> tuple[dict[str, Any], str, str]:

    selected_provider = (
        provider
        or LLM_PROVIDER
    ).strip().lower()

    # --------------------------------------------------
    # Explicit Claude
    # --------------------------------------------------

    if selected_provider == "claude":

        return _call_claude(
            prompt
        )

    # --------------------------------------------------
    # Explicit Hosted LLM
    # --------------------------------------------------

    if selected_provider == "hosted":

        return _call_hosted_llm(
            prompt
        )

    # --------------------------------------------------
    # Explicit Ollama
    # --------------------------------------------------

    if selected_provider == "ollama":

        return _call_ollama(
            prompt
        )

    # --------------------------------------------------
    # Automatic mode
    #
    # Claude first.
    # If Claude fails -> local Ollama.
    # --------------------------------------------------

    if selected_provider == "auto":

        if ANTHROPIC_API_KEY:

            try:

                return _call_claude(
                    prompt
                )

            except Exception as claude_exc:

                try:

                    return _call_ollama(
                        prompt
                    )

                except Exception as ollama_exc:

                    raise LLMError(
                        "Claude failed "
                        f"({claude_exc}); "
                        "Ollama fallback failed "
                        f"({ollama_exc})."
                    ) from ollama_exc

        return _call_ollama(
            prompt
        )

    raise LLMError(
        "Provider must be "
        "'claude', 'hosted', "
        "'ollama', or 'auto'."
    )