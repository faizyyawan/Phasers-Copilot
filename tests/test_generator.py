"""Tests for prompt construction and Ollama answer generation helpers."""

from src.generation.generator import clean_model_answer, source_names
from src.generation.prompt import build_grounded_prompt
from src.retrieval.retriever import RetrievedChunk


def make_chunks() -> list[RetrievedChunk]:
    """Create representative retrieved chunks for generation tests."""
    return [
        RetrievedChunk(
            text="Advance payment is required before confirmation.",
            metadata={
                "source": "payment-policy.md",
                "chunk_id": "payment-policy-chunk-000",
                "header_2": "Advance payment",
            },
            score=0.91,
        ),
        RetrievedChunk(
            text="Payment must be verified before the booking is confirmed.",
            metadata={
                "source": "payment-policy.md",
                "chunk_id": "payment-policy-chunk-001",
                "header_2": "Payment verification",
            },
            score=0.82,
        ),
    ]


def test_build_grounded_prompt_includes_question_and_evidence() -> None:
    prompt = build_grounded_prompt("How much advance must I pay?", make_chunks())

    assert "How much advance must I pay?" in prompt
    assert "payment-policy.md" in prompt
    assert "Advance payment is required" in prompt
    assert "Do not include citations" in prompt


def test_clean_model_answer_removes_think_blocks_and_answer_prefix() -> None:
    answer = clean_model_answer(
        "<think>I should inspect evidence.</think>\n\nAnswer: Refunds need review."
    )

    assert answer == "Refunds need review."


def test_source_names_are_unique_and_preserve_order() -> None:
    chunks = make_chunks() + [
        RetrievedChunk(
            text="Refunds use the original payment method.",
            metadata={"source": "refund-policy.md"},
            score=0.7,
        )
    ]

    assert source_names(chunks) == ["payment-policy.md", "refund-policy.md"]
