"""Tests for top-level support chat orchestration."""

import pytest

import src.rag as rag_module
from src.generation.generator import GeneratedAnswer
from src.retrieval.retriever import RetrievedChunk


def test_greeting_and_thanks_bypass_retrieval(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_retrieve_from_qdrant(**_: object) -> list[RetrievedChunk]:
        raise AssertionError("smalltalk should not call retrieval")

    monkeypatch.setattr(rag_module, "retrieve_from_qdrant", fail_retrieve_from_qdrant)

    assert rag_module.answer_question("hello").route == "greeting"
    assert rag_module.answer_question("thanks").route == "smalltalk_close"


def test_abusive_message_returns_warning_without_retrieval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_retrieve_from_qdrant(**_: object) -> list[RetrievedChunk]:
        raise AssertionError("abusive message should not call retrieval")

    monkeypatch.setattr(rag_module, "retrieve_from_qdrant", fail_retrieve_from_qdrant)

    response = rag_module.answer_question("fuck")

    assert response.route == "abusive_language"
    assert "please avoid abusive or offensive language" in response.answer.answer


def test_out_of_scope_message_returns_refusal_without_retrieval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_retrieve_from_qdrant(**_: object) -> list[RetrievedChunk]:
        raise AssertionError("out-of-scope message should not call retrieval")

    monkeypatch.setattr(rag_module, "retrieve_from_qdrant", fail_retrieve_from_qdrant)

    response = rag_module.answer_question("write me a love poem about the moon")

    assert response.route == "out_of_scope"
    assert "can't help with that kind of request" in response.answer.answer


def test_account_update_returns_safe_workflow_without_generation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_generate_grounded_answer(**_: object) -> GeneratedAnswer:
        raise AssertionError("account update should not call generation")

    monkeypatch.setattr(
        rag_module,
        "generate_grounded_answer",
        fail_generate_grounded_answer,
    )

    response = rag_module.answer_question("how do i change my phone number")

    assert response.route == "account_update"
    assert "can't update account details directly" in response.answer.answer


def test_identity_questions_return_fixed_answers_without_retrieval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_retrieve_from_qdrant(**_: object) -> list[RetrievedChunk]:
        raise AssertionError("identity questions should not call retrieval")

    monkeypatch.setattr(rag_module, "retrieve_from_qdrant", fail_retrieve_from_qdrant)

    bot_response = rag_module.answer_question("who are you")
    user_response = rag_module.answer_question("who am i")

    assert bot_response.route == "bot_identity"
    assert "Embeds Support Copilot" in bot_response.answer.answer
    assert user_response.route == "user_identity"
    assert "can't identify who you are" in user_response.answer.answer


def test_booking_status_uses_mock_tool() -> None:
    response = rag_module.answer_question("What is booking BK-1001 status?")

    assert response.route == "get_booking_status"
    assert "confirmed" in response.answer.answer
    assert response.answer.model == "built-in"


def test_missing_payment_id_asks_for_reference() -> None:
    response = rag_module.answer_question("When is my refund coming?")

    assert response.route == "get_payment_status"
    assert "payment ID" in response.answer.answer


def test_policy_question_uses_retrieval_and_generation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chunks = [
        RetrievedChunk(
            text="Refund eligibility depends on cancellation timing.",
            metadata={"source": "refund-policy.md"},
            score=0.8,
        )
    ]

    monkeypatch.setattr(
        rag_module,
        "retrieve_from_qdrant",
        lambda **_: chunks,
    )
    monkeypatch.setattr(
        rag_module,
        "generate_grounded_answer",
        lambda **_: GeneratedAnswer(
            answer="Refund eligibility depends on cancellation timing.",
            model="qwen3:8b",
            sources=["refund-policy.md"],
        ),
    )

    response = rag_module.answer_question("What is the refund policy?")

    assert response.route == "rag_policy"
    assert response.retrieved_chunks == chunks


def test_empty_evidence_uses_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rag_module, "retrieve_from_qdrant", lambda **_: [])

    response = rag_module.answer_question("Unsupported booking policy question")

    assert response.route == "rag_policy"
    assert "don't have enough policy information" in response.answer.answer
