"""
LLM abstraction layer supporting Ollama, OpenAI, OpenRouter, and Google Gemini.

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
    base_url: str | None = None,
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
    base_url
        Optional base URL override (used for OpenRouter).

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
    if effective_backend == "openrouter":
        return _stream_openai(
            messages, placeholder, start_time,
            model=effective_model,
            temperature=effective_temperature,
            api_key=api_key or config.OPENROUTER_API_KEY or None,
            base_url=base_url or config.OPENROUTER_BASE_URL,
        )
    if effective_backend == "gemini":
        return _stream_gemini(
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
    base_url: str | None = None,
) -> LLMResponse:
    """Stream a response from an OpenAI-compatible API.

    When *base_url* is provided the client points at that endpoint instead of
    the default ``api.openai.com`` — used for OpenRouter and similar services.
    """
    import openai

    client_kwargs: dict = {}
    if api_key:
        client_kwargs["api_key"] = api_key
    if base_url:
        client_kwargs["base_url"] = base_url
    client = openai.OpenAI(**client_kwargs)
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


def _stream_gemini(
    messages: list[dict],
    placeholder,
    start_time: float,
    *,
    model: str,
    temperature: float,
    api_key: str | None = None,
) -> LLMResponse:
    """Stream a response from the Google Gemini API."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key or config.GEMINI_API_KEY)

    # Separate the system instruction from conversational turns.
    system_instruction: str | None = None
    contents: list[types.Content] = []

    for msg in messages:
        role = msg["role"]
        text = msg["content"]
        if role == "system":
            system_instruction = text
        else:
            # Gemini uses "model" where OpenAI uses "assistant".
            gemini_role = "model" if role == "assistant" else "user"
            contents.append(
                types.Content(
                    role=gemini_role,
                    parts=[types.Part.from_text(text=text)],
                ),
            )

    generation_config = types.GenerateContentConfig(
        temperature=temperature,
    )
    if system_instruction:
        generation_config.system_instruction = system_instruction

    full_response = ""
    token_count = 0

    try:
        stream = client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generation_config,
        )
        for chunk in stream:
            if chunk.text:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
    except Exception as exc:
        if not full_response:
            full_response = f"Gemini API error: {exc}"

    placeholder.markdown(full_response)
    latency_ms = int((time.perf_counter() - start_time) * 1000)

    return LLMResponse(
        full_text=full_response,
        token_count=token_count,
        latency_ms=latency_ms,
    )
