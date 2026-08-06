"""Tests for the FastAPI backend."""

from src.api import main as api_main
from src.generation.generator import GeneratedAnswer
from src.rag import RagResponse
from src.retrieval.retriever import RetrievedChunk


def test_health_returns_dependency_state(monkeypatch):
    monkeypatch.setattr(
        api_main,
        "check_qdrant",
        lambda: api_main.ComponentHealth(ok=True, detail="2 indexed chunks"),
    )
    monkeypatch.setattr(
        api_main,
        "check_ollama",
        lambda: api_main.ComponentHealth(ok=True, detail="qwen3:8b available"),
    )

    from fastapi.testclient import TestClient

    client = TestClient(api_main.app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["backend"]["ok"] is True
    assert response.json()["qdrant"]["ok"] is True
    assert response.json()["ollama"]["ok"] is True
    assert response.json()["router"]["ok"] is True
    assert response.json()["model"] == "qwen3:8b"


def test_chat_rejects_empty_message():
    from fastapi.testclient import TestClient

    client = TestClient(api_main.app)
    response = client.post("/api/v1/support/chat", json={"message": "   "})

    assert response.status_code == 422


def test_chat_returns_answer_sources_and_retrieved_chunks(monkeypatch):
    def fake_answer_question(**_: object) -> RagResponse:
        chunk = RetrievedChunk(
            text="Customers must submit a 30% advance payment.",
            metadata={
                "source": "payment-policy.md",
                "chunk_id": "payment-policy-chunk-003",
                "header_2": "Advance Payment",
            },
            score=0.8,
        )
        return RagResponse(
            question="How much advance must I pay?",
            answer=GeneratedAnswer(
                answer="Customers must pay 30% advance.",
                model="qwen3:8b",
                sources=["payment-policy.md"],
            ),
            retrieved_chunks=[chunk],
            route="rag_policy",
            routing_backend="fine_tuned_router",
        )

    monkeypatch.setattr(api_main, "answer_question", fake_answer_question)

    from fastapi.testclient import TestClient

    client = TestClient(api_main.app)
    response = client.post(
        "/api/v1/support/chat",
        json={"message": "How much advance must I pay?", "top_k": 1},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "Customers must pay 30% advance."
    assert payload["route"] == "rag_policy"
    assert payload["routing_backend"] == "fine_tuned_router"
    assert payload["needs_handoff"] is False
    assert "sources" not in payload
    assert "retrieved_chunks" not in payload


def test_chat_returns_debug_sources_and_retrieved_chunks(monkeypatch):
    def fake_answer_question(**_: object) -> RagResponse:
        chunk = RetrievedChunk(
            text="Customers must submit a 30% advance payment.",
            metadata={
                "source": "payment-policy.md",
                "chunk_id": "payment-policy-chunk-003",
                "header_2": "Advance Payment",
            },
            score=0.8,
        )
        return RagResponse(
            question="How much advance must I pay?",
            answer=GeneratedAnswer(
                answer="Customers must pay 30% advance.",
                model="qwen3:8b",
                sources=["payment-policy.md"],
            ),
            retrieved_chunks=[chunk],
            route="rag_policy",
            routing_backend="fine_tuned_router",
        )

    monkeypatch.setattr(api_main, "answer_question", fake_answer_question)

    from fastapi.testclient import TestClient

    client = TestClient(api_main.app)
    response = client.post(
        "/api/v1/support/chat",
        json={
            "message": "How much advance must I pay?",
            "top_k": 1,
            "debug": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sources"] == ["payment-policy.md"]
    assert payload["routing_backend"] == "fine_tuned_router"
    assert payload["retrieved_chunks"][0]["source"] == "payment-policy.md"
    assert payload["retrieved_chunks"][0]["section"] == "Advance Payment"


def test_chat_replies_to_greeting_without_retrieval(monkeypatch):
    import src.rag as rag_module

    def fail_retrieve_from_qdrant(**_: object) -> list[RetrievedChunk]:
        raise AssertionError("greeting should not call retrieval")

    monkeypatch.setattr(rag_module, "retrieve_from_qdrant", fail_retrieve_from_qdrant)

    from fastapi.testclient import TestClient

    client = TestClient(api_main.app)
    response = client.post("/api/v1/support/chat", json={"message": "hello"})

    assert response.status_code == 200
    payload = response.json()
    assert "Hi!" in payload["answer"]
    assert payload["route"] == "greeting"
    assert "sources" not in payload
    assert "retrieved_chunks" not in payload
