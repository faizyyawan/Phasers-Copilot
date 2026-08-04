"""Generate grounded answers with a local Ollama model."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import requests

from ..retrieval.retriever import RetrievedChunk
from ..safety.profanity import censor_abusive_words
from .prompt import SYSTEM_PROMPT, build_grounded_prompt

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen3:8b"
DEFAULT_TIMEOUT_SECONDS = 120
THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)
SOURCE_LABEL_RE = re.compile(
    r"\s*(?:\(|\[)?(?:source|sources|evidence|chunk)s?:?[^.\n]*\.md(?:\)|\])?",
    re.IGNORECASE,
)
MARKDOWN_FILE_RE = re.compile(r"\s*\(?[A-Za-z0-9_-]+\.md\)?")


@dataclass(frozen=True)
class GeneratedAnswer:
    """Generated answer plus the evidence that was supplied to the model."""

    answer: str
    model: str
    sources: list[str]


def source_names(chunks: Sequence[RetrievedChunk]) -> list[str]:
    """Return unique source names in retrieval order."""
    sources: list[str] = []
    for chunk in chunks:
        source = chunk.metadata.get("source")
        if isinstance(source, str) and source not in sources:
            sources.append(source)
    return sources


def clean_model_answer(answer: str) -> str:
    """Remove model-only artifacts from customer-visible answer text."""
    cleaned = THINK_BLOCK_RE.sub("", answer)
    cleaned = re.sub(r"^\s*Answer:\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = SOURCE_LABEL_RE.sub("", cleaned)
    cleaned = MARKDOWN_FILE_RE.sub("", cleaned)
    cleaned = cleaned.strip()
    if not cleaned:
        raise RuntimeError("Ollama response did not include non-empty customer text.")
    return censor_abusive_words(cleaned)


def ollama_chat(
    prompt: str,
    model: str = DEFAULT_OLLAMA_MODEL,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> str:
    """Send one grounded prompt to Ollama's local chat API."""
    if not prompt.strip():
        raise ValueError("prompt must not be empty.")
    if not model.strip():
        raise ValueError("model must not be empty.")

    response = requests.post(
        f"{ollama_url.rstrip('/')}/api/chat",
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        },
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    payload: dict[str, Any] = response.json()

    message = payload.get("message")
    if not isinstance(message, dict):
        raise TypeError("Ollama response did not include a message object.")

    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Ollama response did not include non-empty content.")
    return clean_model_answer(content)


def generate_grounded_answer(
    question: str,
    chunks: Sequence[RetrievedChunk],
    model: str = DEFAULT_OLLAMA_MODEL,
    ollama_url: str = DEFAULT_OLLAMA_URL,
) -> GeneratedAnswer:
    """Generate an answer from retrieved evidence."""
    prompt = build_grounded_prompt(question=question, chunks=chunks)
    answer = ollama_chat(prompt=prompt, model=model, ollama_url=ollama_url)
    return GeneratedAnswer(
        answer=answer,
        model=model,
        sources=source_names(chunks),
    )
