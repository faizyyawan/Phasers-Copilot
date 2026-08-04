"""Tests for dense retrieval from Qdrant."""

import numpy as np
import pytest
from qdrant_client import QdrantClient

from src.embeddings.embed_documents import EmbeddedChunk
from src.ingestion.index_documents import COLLECTION_NAME, index_embedded_chunks
from src.retrieval.retriever import (
    RetrievedChunk,
    embed_query,
    retrieve_chunks,
    validate_top_k,
)


class FakeEmbeddingModel:
    """Deterministic query embedding model for retrieval tests."""

    def encode(self, texts: list[str], **_: object) -> np.ndarray:
        text = texts[0].lower()
        if "refund" in text:
            return np.asarray([[0.0, 1.0, 0.0]], dtype=np.float32)
        return np.asarray([[1.0, 0.0, 0.0]], dtype=np.float32)


def make_embedded_chunks() -> list[EmbeddedChunk]:
    """Create small vectors that make nearest-neighbor behavior obvious."""
    return [
        EmbeddedChunk(
            text="Advance payments must be verified before confirmation.",
            metadata={
                "chunk_id": "payment-policy-chunk-000",
                "document_id": "payment-policy",
                "source": "payment-policy.md",
                "chunk_index": 0,
            },
            embedding=[1.0, 0.0, 0.0],
        ),
        EmbeddedChunk(
            text="Eligible refunds return to the original payment method.",
            metadata={
                "chunk_id": "refund-policy-chunk-000",
                "document_id": "refund-policy",
                "source": "refund-policy.md",
                "chunk_index": 0,
            },
            embedding=[0.0, 1.0, 0.0],
        ),
    ]


def test_embed_query_returns_one_vector() -> None:
    vector = embed_query("How much advance must I pay?", FakeEmbeddingModel())  # type: ignore[arg-type]

    assert vector == [1.0, 0.0, 0.0]


def test_retrieve_chunks_returns_ranked_chunks_with_payload_text_removed() -> None:
    client = QdrantClient(":memory:")
    index_embedded_chunks(client, make_embedded_chunks())

    results = retrieve_chunks(
        question="How do refunds work?",
        client=client,
        model=FakeEmbeddingModel(),  # type: ignore[arg-type]
        collection_name=COLLECTION_NAME,
        top_k=1,
    )

    assert len(results) == 1
    assert isinstance(results[0], RetrievedChunk)
    assert results[0].text == "Eligible refunds return to the original payment method."
    assert results[0].metadata["source"] == "refund-policy.md"
    assert "text" not in results[0].metadata
    assert results[0].score == pytest.approx(1.0)


def test_validate_top_k_rejects_non_positive_values() -> None:
    with pytest.raises(ValueError, match="top_k"):
        validate_top_k(0)
