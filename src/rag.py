"""RAG orchestration entry point."""

from __future__ import annotations

import argparse
from dataclasses import dataclass

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
from .routing.router import RouteDecision, route_message
from .support.responses import (
    GREETING_ANSWER,
    SMALLTALK_CLOSE_ANSWER,
    booking_status_answer,
    handoff_answer,
    missing_identifier_answer,
    no_evidence_answer,
    notification_history_answer,
    payment_status_answer,
    tickets_answer,
)
from .tools.mock_support_tools import (
    get_booking_status,
    get_notification_history,
    get_payment_status,
    search_previous_tickets,
)

BUILT_IN_MODEL_NAME = "built-in"
LOW_CONFIDENCE_SCORE = 0.15
BROAD_POLICY_TERMS = (
    "refund policy",
    "cancellation policy",
    "payment policy",
    "booking policy",
)
BROAD_POLICY_TOP_K = 8


@dataclass(frozen=True)
class RagResponse:
    """The complete output of one local RAG run."""

    question: str
    answer: GeneratedAnswer
    retrieved_chunks: list[RetrievedChunk]
    route: str
    needs_handoff: bool = False
    handoff_reason: str | None = None


def _built_in_response(
    question: str,
    decision: RouteDecision,
    answer: str,
    needs_handoff: bool = False,
) -> RagResponse:
    """Return a deterministic response without retrieval or generation."""
    return RagResponse(
        question=question,
        answer=GeneratedAnswer(answer=answer, model=BUILT_IN_MODEL_NAME, sources=[]),
        retrieved_chunks=[],
        route=decision.route,
        needs_handoff=needs_handoff,
        handoff_reason=decision.handoff_reason,
    )


def answer_question(
    question: str,
    qdrant_url: str | None = DEFAULT_QDRANT_URL,
    top_k: int = DEFAULT_TOP_K,
    ollama_model: str = DEFAULT_OLLAMA_MODEL,
    ollama_url: str = DEFAULT_OLLAMA_URL,
) -> RagResponse:
    """Retrieve evidence and ask Ollama to produce a grounded answer."""
    decision = route_message(question)
    entities = decision.entities

    if decision.route == "greeting":
        return _built_in_response(question, decision, GREETING_ANSWER)
    if decision.route == "smalltalk_close":
        return _built_in_response(question, decision, SMALLTALK_CLOSE_ANSWER)
    if decision.route == "human_escalation":
        return _built_in_response(
            question,
            decision,
            handoff_answer(decision.handoff_reason),
            needs_handoff=True,
        )
    if decision.route == "get_booking_status":
        booking_id = entities.get("booking_id")
        if not booking_id:
            return _built_in_response(
                question,
                decision,
                missing_identifier_answer(decision.route),
            )
        return _built_in_response(
            question,
            decision,
            booking_status_answer(get_booking_status(booking_id), booking_id),
        )
    if decision.route == "get_payment_status":
        payment_id = entities.get("payment_id")
        booking_id = entities.get("booking_id")
        if not payment_id and not booking_id:
            return _built_in_response(
                question,
                decision,
                missing_identifier_answer(decision.route),
            )
        reference = payment_id or booking_id or "that reference"
        return _built_in_response(
            question,
            decision,
            payment_status_answer(
                get_payment_status(payment_id=payment_id, booking_id=booking_id),
                reference,
            ),
        )
    if decision.route == "get_notification_history":
        notification_id = entities.get("notification_id")
        booking_id = entities.get("booking_id")
        if not notification_id and not booking_id:
            return _built_in_response(
                question,
                decision,
                missing_identifier_answer(decision.route),
            )
        reference = notification_id or booking_id or "that reference"
        return _built_in_response(
            question,
            decision,
            notification_history_answer(
                get_notification_history(
                    notification_id=notification_id,
                    booking_id=booking_id,
                ),
                reference,
            ),
        )
    if decision.route == "search_previous_tickets":
        ticket_id = entities.get("ticket_id")
        booking_id = entities.get("booking_id")
        topic = "refund" if "refund" in question.lower() else None
        if not ticket_id and not booking_id and not topic:
            return _built_in_response(
                question,
                decision,
                missing_identifier_answer(decision.route),
            )
        reference = ticket_id or booking_id or topic or "that topic"
        return _built_in_response(
            question,
            decision,
            tickets_answer(
                search_previous_tickets(
                    ticket_id=ticket_id,
                    booking_id=booking_id,
                    topic=topic,
                ),
                reference,
            ),
        )
    if decision.route == "get_court_availability":
        return _built_in_response(
            question,
            decision,
            missing_identifier_answer(decision.route),
        )

    effective_top_k = top_k
    if any(term in question.lower() for term in BROAD_POLICY_TERMS):
        effective_top_k = max(top_k, BROAD_POLICY_TOP_K)

    chunks = retrieve_from_qdrant(
        question=question,
        qdrant_url=qdrant_url,
        top_k=effective_top_k,
    )
    if not chunks or max(chunk.score for chunk in chunks) < LOW_CONFIDENCE_SCORE:
        return _built_in_response(question, decision, no_evidence_answer())

    answer = generate_grounded_answer(
        question=question,
        chunks=chunks,
        model=ollama_model,
        ollama_url=ollama_url,
    )
    return RagResponse(
        question=question,
        answer=answer,
        retrieved_chunks=chunks,
        route=decision.route,
    )


def format_rag_response(response: RagResponse) -> str:
    """Format the answer and retrieved sources for CLI output."""
    lines = [
        "Answer:",
        response.answer.answer,
        "",
        f"Route: {response.route}",
        f"Needs handoff: {response.needs_handoff}",
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
