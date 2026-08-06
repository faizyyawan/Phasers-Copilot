"""Tests for storing embedded knowledge chunks in Qdrant."""

import math

import pytest
from qdrant_client import QdrantClient, models

from src.embeddings.embed_documents import EmbeddedChunk
from src.ingestion.index_documents import (
    COLLECTION_NAME,
    index_embedded_chunks,
    parse_args,
    qdrant_point_id,
    validate_embedded_chunks,
)


def make_embedded_chunks() -> list[EmbeddedChunk]:
    """Create small deterministic vectors and representative metadata."""
    return [
        EmbeddedChunk(
            text="Advance payments must be verified before confirmation.",
            metadata={
                "chunk_id": "payment-policy-chunk-000",
                "document_id": "payment-policy",
                "source": "payment-policy.md",
                "chunk_index": 0,
                "header_1": "Payment Policy",
            },
            embedding=[1.0, 0.0, 0.5],
        ),
        EmbeddedChunk(
            text="Eligible refunds return to the original payment method.",
            metadata={
                "chunk_id": "refund-policy-chunk-000",
                "document_id": "refund-policy",
                "source": "refund-policy.md",
                "chunk_index": 0,
                "header_1": "Refund Policy",
            },
            embedding=[0.0, 1.0, 0.5],
        ),
    ]


def stored_points(client: QdrantClient) -> list[models.Record]:
    """Return every stored test point with its payload and vector."""
    points, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=100,
        with_payload=True,
        with_vectors=True,
    )
    return points


def test_indexing_creates_cosine_collection_with_derived_dimension() -> None:
    client = QdrantClient(":memory:")

    point_count = index_embedded_chunks(client, make_embedded_chunks())

    collection = client.get_collection(COLLECTION_NAME)
    vectors = collection.config.params.vectors
    assert isinstance(vectors, models.VectorParams)
    assert vectors.size == 3
    assert vectors.distance == models.Distance.COSINE
    assert point_count == 2
    assert client.count(COLLECTION_NAME, exact=True).count == 2


def test_indexing_preserves_text_and_all_metadata() -> None:
    client = QdrantClient(":memory:")
    chunks = make_embedded_chunks()

    index_embedded_chunks(client, chunks)

    points_by_id = {str(point.id): point for point in stored_points(client)}
    first = points_by_id[qdrant_point_id("payment-policy-chunk-000")]
    assert first.payload == {
        **chunks[0].metadata,
        "text": chunks[0].text,
    }
    vector_norm = math.sqrt(sum(value**2 for value in chunks[0].embedding))
    normalized_embedding = [value / vector_norm for value in chunks[0].embedding]
    assert first.vector == pytest.approx(normalized_embedding)


def test_repeated_indexing_replaces_collection_without_duplicates() -> None:
    client = QdrantClient(":memory:")
    chunks = make_embedded_chunks()

    index_embedded_chunks(client, chunks)
    first_ids = {str(point.id) for point in stored_points(client)}
    index_embedded_chunks(client, chunks)
    second_ids = {str(point.id) for point in stored_points(client)}

    assert first_ids == second_ids
    assert second_ids == {
        qdrant_point_id("payment-policy-chunk-000"),
        qdrant_point_id("refund-policy-chunk-000"),
    }
    assert client.count(COLLECTION_NAME, exact=True).count == len(chunks)


def test_validation_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="empty embedded chunk"):
        validate_embedded_chunks([])


def test_validation_rejects_inconsistent_dimensions() -> None:
    chunks = make_embedded_chunks()
    chunks[1] = EmbeddedChunk(
        text=chunks[1].text,
        metadata=chunks[1].metadata,
        embedding=[0.0, 1.0],
    )

    with pytest.raises(ValueError, match="same dimension"):
        validate_embedded_chunks(chunks)


@pytest.mark.parametrize("invalid_value", [math.nan, math.inf, -math.inf])
def test_validation_rejects_non_finite_embeddings(invalid_value: float) -> None:
    chunks = make_embedded_chunks()
    chunks[0] = EmbeddedChunk(
        text=chunks[0].text,
        metadata=chunks[0].metadata,
        embedding=[invalid_value, 0.0, 0.5],
    )

    with pytest.raises(ValueError, match="NaN or infinite"):
        validate_embedded_chunks(chunks)


def test_qdrant_url_command_line_option_is_optional() -> None:
    assert parse_args([]).qdrant_url is None
    assert parse_args(
        ["--qdrant-url", "http://localhost:6333"]
    ).qdrant_url == "http://localhost:6333"
