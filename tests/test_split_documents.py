"""Tests for the document chunking stage."""

import pytest
from langchain_core.documents import Document

from src.ingestion.load_documents import load_documents
from src.ingestion.split_documents import split_documents


def make_document(document_id: str = "sample") -> Document:
    """Create a small Markdown document for splitter tests."""
    return Document(
        page_content=(
            "# Sample Document\n\n"
            "This is the first paragraph used for chunking tests.\n\n"
            "## Details\n\n"
            "This second paragraph gives the splitter enough text to work with."
        ),
        metadata={
            "source": f"{document_id}.md",
            "document_id": document_id,
            "file_type": "markdown",
        },
    )


def test_document_is_split_into_one_or_more_chunks() -> None:
    chunks = split_documents([make_document()])

    assert len(chunks) >= 1


def test_every_chunk_is_langchain_document() -> None:
    chunks = split_documents([make_document()])

    assert all(isinstance(chunk, Document) for chunk in chunks)


def test_original_metadata_is_preserved() -> None:
    document = make_document("booking-process")
    chunks = split_documents([document])

    for chunk in chunks:
        assert chunk.metadata["source"] == "booking-process.md"
        assert chunk.metadata["document_id"] == "booking-process"
        assert chunk.metadata["file_type"] == "markdown"


def test_chunk_index_starts_from_zero_for_each_document() -> None:
    chunks = split_documents([make_document("first"), make_document("second")])

    first_indexes = [
        chunk.metadata["chunk_index"]
        for chunk in chunks
        if chunk.metadata["document_id"] == "first"
    ]
    second_indexes = [
        chunk.metadata["chunk_index"]
        for chunk in chunks
        if chunk.metadata["document_id"] == "second"
    ]

    assert first_indexes[0] == 0
    assert second_indexes[0] == 0


def test_chunk_id_values_are_unique() -> None:
    chunks = split_documents([make_document("first"), make_document("second")])
    chunk_ids = [chunk.metadata["chunk_id"] for chunk in chunks]

    assert len(chunk_ids) == len(set(chunk_ids))


def test_empty_chunks_are_not_produced() -> None:
    chunks = split_documents([make_document()])

    assert all(chunk.page_content.strip() for chunk in chunks)


def test_chunk_overlap_validation_works() -> None:
    with pytest.raises(ValueError, match="chunk_overlap must be smaller"):
        split_documents([make_document()], chunk_size=100, chunk_overlap=100)


def test_original_input_document_metadata_is_not_mutated() -> None:
    document = make_document()
    original_metadata = dict(document.metadata)

    split_documents([document])

    assert document.metadata == original_metadata
    assert "chunk_index" not in document.metadata
    assert "chunk_id" not in document.metadata


def test_multiple_documents_receive_independent_chunk_indexes() -> None:
    first = make_document("first")
    second = make_document("second")

    chunks = split_documents([first, second], chunk_size=80, chunk_overlap=20)

    first_indexes = [
        chunk.metadata["chunk_index"]
        for chunk in chunks
        if chunk.metadata["document_id"] == "first"
    ]
    second_indexes = [
        chunk.metadata["chunk_index"]
        for chunk in chunks
        if chunk.metadata["document_id"] == "second"
    ]

    assert first_indexes == list(range(len(first_indexes)))
    assert second_indexes == list(range(len(second_indexes)))


def test_real_knowledge_base_loads_and_splits_successfully() -> None:
    documents = load_documents()
    chunks = split_documents(documents)

    assert len(documents) == 10
    assert len(chunks) >= len(documents)
    assert all(isinstance(chunk, Document) for chunk in chunks)
    assert all(chunk.page_content.strip() for chunk in chunks)
