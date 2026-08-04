"""Prompt definitions for grounded support answers."""

from __future__ import annotations

from collections.abc import Sequence

from ..retrieval.retriever import RetrievedChunk


SYSTEM_PROMPT = """You are Embeds Support Copilot, a friendly customer support chatbot.
Answer only from the provided evidence, but write like a helpful human support agent.
Use complete, natural sentences.
Do not mention sources, files, chunks, evidence, or retrieval.
Do not cite source file names.
If the evidence is not enough, say what information is needed instead of guessing.
If the question needs a live booking, payment, notification, or ticket lookup,
explain that a support agent or system lookup is needed."""


def format_evidence(chunks: Sequence[RetrievedChunk]) -> str:
    """Format retrieved chunks as compact cited evidence blocks."""
    if not chunks:
        return "No evidence was retrieved."

    evidence_blocks: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        source = chunk.metadata.get("source", "unknown-source")
        section = (
            chunk.metadata.get("header_3")
            or chunk.metadata.get("header_2")
            or chunk.metadata.get("header_1")
            or "Untitled section"
        )
        evidence_blocks.append(
            "\n".join(
                [
                    f"[{index}] Source: {source}",
                    f"Section: {section}",
                    f"Text: {chunk.text}",
                ]
            )
        )
    return "\n\n".join(evidence_blocks)


def build_grounded_prompt(question: str, chunks: Sequence[RetrievedChunk]) -> str:
    """Build the user prompt sent to the local LLM."""
    return "\n\n".join(
        [
            "Use the evidence below to answer the support question.",
            "Write a conversational answer for the customer.",
            "Do not include citations, source names, file names, or evidence labels.",
            f"Question: {question}",
            "Evidence:",
            format_evidence(chunks),
            "Answer:",
        ]
    )
