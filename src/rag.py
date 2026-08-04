"""RAG orchestration entry point."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import re

from .generation.generator import (
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OLLAMA_URL,
    GeneratedAnswer,
    generate_grounded_answer,
)
from .retrieval.retriever import (
    DEFAULT_QDRANT_URL,
    DEFAULT_TOP_K,
    RetrievedChunk,
    retrieve_from_qdrant,
)

GREETING_RE = re.compile(
    r"^\s*(hi|hello|hey|yo|salam|assalam(?:\s+o\s+alaikum)?|good\s+"
    r"(morning|afternoon|evening))[\s!.?,]*$",
    re.IGNORECASE,
)
GREETING_ANSWER = (
    "Hi! I can help with bookings, payments, refunds, cancellations, account "
    "questions, and troubleshooting. What would you like to know?"
)


def is_greeting(message: str) -> bool:
    """Return whether the message is only a greeting."""
    return GREETING_RE.fullmatch(message) is not None


@dataclass(frozen=True)
class RagResponse:
    """The complete output of one local RAG run."""

    question: str
    answer: GeneratedAnswer
    retrieved_chunks: list[RetrievedChunk]


def answer_question(
    question: str,
    qdrant_url: str | None = DEFAULT_QDRANT_URL,
    top_k: int = DEFAULT_TOP_K,
    ollama_model: str = DEFAULT_OLLAMA_MODEL,
    ollama_url: str = DEFAULT_OLLAMA_URL,
) -> RagResponse:
    """Retrieve evidence and ask Ollama to produce a grounded answer."""
    if is_greeting(question):
        return RagResponse(
            question=question,
            answer=GeneratedAnswer(
                answer=GREETING_ANSWER,
                model="built-in",
                sources=[],
            ),
            retrieved_chunks=[],
        )

    chunks = retrieve_from_qdrant(
        question=question,
        qdrant_url=qdrant_url,
        top_k=top_k,
    )
    answer = generate_grounded_answer(
        question=question,
        chunks=chunks,
        model=ollama_model,
        ollama_url=ollama_url,
    )
    return RagResponse(question=question, answer=answer, retrieved_chunks=chunks)


def format_rag_response(response: RagResponse) -> str:
    """Format the answer and retrieved sources for CLI output."""
    lines = [
        "Answer:",
        response.answer.answer,
        "",
        "Sources:",
    ]
    if response.answer.sources:
        lines.extend(f"- {source}" for source in response.answer.sources)
    else:
        lines.append("- No sources retrieved")

    lines.extend(["", "Retrieved chunks:"])
    for index, chunk in enumerate(response.retrieved_chunks, start=1):
        source = chunk.metadata.get("source", "unknown-source")
        chunk_id = chunk.metadata.get("chunk_id", "unknown-chunk")
        lines.append(f"{index}. {source} / {chunk_id} / score {chunk.score:.4f}")
    return "\n".join(lines)


def parse_args(arguments: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line options for a local RAG answer."""
    parser = argparse.ArgumentParser(description="Ask the local RAG pipeline.")
    parser.add_argument("question", help="Support question to answer.")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--qdrant-url", default=DEFAULT_QDRANT_URL)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--ollama-model", default=DEFAULT_OLLAMA_MODEL)
    parser.add_argument(
        "--local-qdrant",
        action="store_true",
        help="Use embedded Qdrant storage at data/qdrant instead of localhost.",
    )
    return parser.parse_args(arguments)


def main() -> None:
    """Run retrieval plus Ollama generation for one question."""
    arguments = parse_args()
    response = answer_question(
        question=arguments.question,
        qdrant_url=None if arguments.local_qdrant else arguments.qdrant_url,
        top_k=arguments.top_k,
        ollama_model=arguments.ollama_model,
        ollama_url=arguments.ollama_url,
    )
    print(format_rag_response(response))


if __name__ == "__main__":
    main()
