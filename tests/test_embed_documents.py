"""Unit tests for embedding generation validation and metadata preservation."""

import numpy as np
import pytest
from langchain_core.documents import Document

from src.embeddings.embed_documents import (
    EmbeddedChunk,
    embed_chunks,
    select_device,
    validate_embedding_matrix,
)


class FakeEmbeddingModel:
    """Small deterministic model substitute that avoids network access in tests."""

    def encode(self, texts: list[str], **_: object) -> np.ndarray:
        return np.asarray(
            [[float(index), float(len(text)), 1.0] for index, text in enumerate(texts)],
            dtype=np.float32,
        )


def make_chunks() -> list[Document]:
    """Create representative chunks with metadata for embedding tests."""
    return [
        Document(
            page_content="First chunk",
            metadata={"document_id": "first", "chunk_id": "first-chunk-000"},
        ),
        Document(
            page_content="Second chunk",
            metadata={"document_id": "second", "chunk_id": "second-chunk-000"},
        ),
    ]


def test_embed_chunks_returns_one_embedding_per_chunk_in_input_order() -> None:
    chunks = make_chunks()

    embedded_chunks = embed_chunks(chunks, model=FakeEmbeddingModel(), batch_size=2)  # type: ignore[arg-type]

    assert len(embedded_chunks) == len(chunks)
    assert all(isinstance(chunk, EmbeddedChunk) for chunk in embedded_chunks)
    assert [chunk.text for chunk in embedded_chunks] == [chunk.page_content for chunk in chunks]
    assert [chunk.embedding[0] for chunk in embedded_chunks] == [0.0, 1.0]


def test_embed_chunks_preserves_metadata_without_mutating_input() -> None:
    chunks = make_chunks()
    original_metadata = [dict(chunk.metadata) for chunk in chunks]

    embedded_chunks = embed_chunks(chunks, model=FakeEmbeddingModel())  # type: ignore[arg-type]

    assert [chunk.metadata for chunk in embedded_chunks] == original_metadata
    assert [chunk.metadata for chunk in chunks] == original_metadata
    assert embedded_chunks[0].metadata is not chunks[0].metadata


def test_embedding_validation_rejects_nan_and_count_mismatch() -> None:
    with pytest.raises(ValueError, match="NaN or infinite"):
        validate_embedding_matrix(np.asarray([[np.nan, 1.0]]), expected_count=1)

    with pytest.raises(ValueError, match="does not match chunk count"):
        validate_embedding_matrix(np.asarray([[1.0, 2.0]]), expected_count=2)


def test_select_device_returns_supported_device_name() -> None:
    assert select_device() in {"cpu", "cuda"}
