"""
Minimal, provider-agnostic LLM client used by the Streamlit app.

Supports:
  - OpenAI (cloud, needs an API key)
  - Ollama (local models, needs Ollama running on the machine)
"""

from __future__ import annotations
from typing import List, Dict, Iterator


class LLMError(Exception):
    """Raised when a provider fails to answer."""


def ask_openai(
    messages: List[Dict[str, str]],
    api_key: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    stream: bool = True,
):
    from openai import OpenAI

    if not api_key:
        raise LLMError("No OpenAI API key was provided.")

    client = OpenAI(api_key=api_key)

    if stream:
        def _gen() -> Iterator[str]:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )
            for chunk in resp:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta

        return _gen()

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content


def ask_ollama(
    messages: List[Dict[str, str]],
    model: str = "llama3",
    temperature: float = 0.7,
    stream: bool = True,
    host: str | None = None,
):
    import ollama

    client = ollama.Client(host=host) if host else ollama

    if stream:
        def _gen() -> Iterator[str]:
            try:
                for chunk in client.chat(
                    model=model,
                    messages=messages,
                    options={"temperature": temperature},
                    stream=True,
                ):
                    piece = chunk.get("message", {}).get("content", "")
                    if piece:
                        yield piece
            except Exception as e:  # ollama not running, model missing, etc.
                raise LLMError(str(e))

        return _gen()

    try:
        resp = client.chat(
            model=model,
            messages=messages,
            options={"temperature": temperature},
        )
        return resp["message"]["content"]
    except Exception as e:
        raise LLMError(str(e))


def ask(
    provider: str,
    messages: List[Dict[str, str]],
    *,
    api_key: str = "",
    model: str = "",
    temperature: float = 0.7,
    stream: bool = True,
    ollama_host: str | None = None,
):
    """Route a chat request to the selected provider."""
    if provider == "OpenAI":
        return ask_openai(
            messages,
            api_key=api_key,
            model=model or "gpt-4o-mini",
            temperature=temperature,
            stream=stream,
        )
    elif provider == "Ollama (local)":
        return ask_ollama(
            messages,
            model=model or "llama3",
            temperature=temperature,
            stream=stream,
            host=ollama_host,
        )
    else:
        raise LLMError(f"Unknown provider: {provider}")
