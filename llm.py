"""
LLM abstraction layer supporting Ollama (local dev) and OpenAI (production).

This module provides a unified interface for sending chat messages and
streaming responses, capturing per-response metadata (token count, latency)
required by the frozen-spec logging schema (§5.1).
"""

import json
import time
from dataclasses import dataclass

import requests

import config


@dataclass
class LLMResponse:
    """Metadata for a single LLM response."""

    full_text: str
    token_count: int
    latency_ms: int


def stream_chat(
    messages: list[dict],
    placeholder,
    *,
    backend: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
    api_key: str | None = None,
) -> LLMResponse:
    """Send messages to the configured LLM backend, stream into placeholder.

    Parameters
    ----------
    messages : list[dict]
        OpenAI-style message list (role/content pairs).
    placeholder
        A Streamlit ``st.empty()`` widget for incremental display.
    backend, model, temperature, api_key
        Optional overrides (used by dev-mode sidebar). Falls back to
        ``config.*`` / env-var defaults when *None*.

    Returns
    -------
    LLMResponse
        The complete response with metadata.
    """
    effective_backend = backend or config.BACKEND
    effective_model = model or config.MODEL
    effective_temperature = temperature if temperature is not None else config.TEMPERATURE
    start_time = time.perf_counter()

    if effective_backend == "openai":
        return _stream_openai(
            messages, placeholder, start_time,
            model=effective_model,
            temperature=effective_temperature,
            api_key=api_key,
        )
    return _stream_ollama(
        messages, placeholder, start_time,
        model=effective_model,
        temperature=effective_temperature,
    )


def _stream_ollama(
    messages: list[dict],
    placeholder,
    start_time: float,
    *,
    model: str,
    temperature: float,
) -> LLMResponse:
    """Stream a response from Ollama."""
    url = f"{config.OLLAMA_HOST}/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {"temperature": temperature},
    }

    full_response = ""
    token_count = 0

    try:
        with requests.post(url, json=payload, stream=True, timeout=120) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                chunk = json.loads(line)
                token = chunk.get("message", {}).get("content", "")
                full_response += token
                placeholder.markdown(full_response + "▌")

                # Ollama returns eval_count in the final chunk.
                if chunk.get("done"):
                    token_count = chunk.get("eval_count", 0)
    except requests.ConnectionError:
        full_response = (
            "I'm sorry — I cannot reach the language model right now. "
            "Please make sure Ollama is running and try again."
        )
    except requests.HTTPError as exc:
        full_response = (
            f"The language model returned an error (HTTP {exc.response.status_code}). "
            "Please check that the model is loaded in Ollama."
        )
    except requests.Timeout:
        full_response = (
            "The request to the language model timed out. "
            "Please try again in a moment."
        )

    placeholder.markdown(full_response)
    latency_ms = int((time.perf_counter() - start_time) * 1000)

    return LLMResponse(
        full_text=full_response,
        token_count=token_count,
        latency_ms=latency_ms,
    )


def _stream_openai(
    messages: list[dict],
    placeholder,
    start_time: float,
    *,
    model: str,
    temperature: float,
    api_key: str | None = None,
) -> LLMResponse:
    """Stream a response from the OpenAI API."""
    import openai

    client = openai.OpenAI(api_key=api_key) if api_key else openai.OpenAI()
    full_response = ""
    token_count = 0

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=True,
            stream_options={"include_usage": True},
        )

        for chunk in stream:
            if chunk.usage is not None:
                token_count = chunk.usage.completion_tokens or 0

            if chunk.choices:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    full_response += delta.content
                    placeholder.markdown(full_response + "▌")
    except Exception as exc:
        if not full_response:
            full_response = f"OpenAI API error: {exc}"

    placeholder.markdown(full_response)
    latency_ms = int((time.perf_counter() - start_time) * 1000)

    return LLMResponse(
        full_text=full_response,
        token_count=token_count,
        latency_ms=latency_ms,
    )
