"""Store embedded knowledge-base chunks in a local Qdrant collection."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import NAMESPACE_URL, uuid5

import numpy as np
from qdrant_client import QdrantClient, models

from ..embeddings.embed_documents import (
    BATCH_SIZE,
    MODEL_NAME,
    EmbeddedChunk,
    run_embedding_pipeline,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_QDRANT_PATH = PROJECT_ROOT / "data" / "qdrant"
COLLECTION_NAME = "knowledge_chunks"
REQUIRED_METADATA_FIELDS = ("chunk_id", "document_id", "source", "chunk_index")


@dataclass(frozen=True)
class IndexingRun:
    """Measurements and identifiers from one complete indexing run."""

    collection_name: str
    storage_location: str
    point_count: int
    embedding_dimension: int
    model_name: str
    device: str
    elapsed_seconds: float


def qdrant_point_id(chunk_id: str) -> str:
    """Return the stable UUID used as Qdrant's point ID for a chunk."""
    return str(uuid5(NAMESPACE_URL, f"embeds-support-copilot:{chunk_id}"))


def validate_embedded_chunks(embedded_chunks: Sequence[EmbeddedChunk]) -> int:
    """Validate index-ready chunks and return their shared vector dimension."""
    if not embedded_chunks:
        raise ValueError("Cannot index an empty embedded chunk collection.")

    expected_dimension: int | None = None
    seen_chunk_ids: set[str] = set()

    for index, chunk in enumerate(embedded_chunks):
        if not isinstance(chunk, EmbeddedChunk):
            raise TypeError(f"embedded_chunks[{index}] must be an EmbeddedChunk.")
        if not chunk.text.strip():
            raise ValueError(f"embedded_chunks[{index}] has empty text.")

        missing_fields = [
            field for field in REQUIRED_METADATA_FIELDS if field not in chunk.metadata
        ]
        if missing_fields:
            fields = ", ".join(missing_fields)
            raise ValueError(
                f"embedded_chunks[{index}] is missing required metadata: {fields}."
            )

        chunk_id = chunk.metadata["chunk_id"]
        if not isinstance(chunk_id, str) or not chunk_id.strip():
            raise ValueError(
                f"embedded_chunks[{index}] metadata must contain a non-empty chunk_id."
            )
        if chunk_id in seen_chunk_ids:
            raise ValueError(f"Duplicate chunk_id cannot be indexed: {chunk_id}.")
        seen_chunk_ids.add(chunk_id)

        if not chunk.embedding:
            raise ValueError(f"embedded_chunks[{index}] has an empty embedding.")
        if expected_dimension is None:
            expected_dimension = len(chunk.embedding)
        elif len(chunk.embedding) != expected_dimension:
            raise ValueError(
                "All embeddings must have the same dimension; "
                f"embedded_chunks[{index}] has {len(chunk.embedding)}, expected "
                f"{expected_dimension}."
            )

        embedding = np.asarray(chunk.embedding, dtype=np.float32)
        if embedding.ndim != 1 or not np.isfinite(embedding).all():
            raise ValueError(
                f"embedded_chunks[{index}] embedding contains NaN or infinite values."
            )

    if expected_dimension is None:
        raise ValueError("Could not determine the embedding dimension.")
    return expected_dimension


def _point_from_chunk(chunk: EmbeddedChunk) -> models.PointStruct:
    """Convert one embedded chunk to Qdrant's point representation."""
    payload: dict[str, Any] = {**chunk.metadata, "text": chunk.text}
    chunk_id = str(chunk.metadata["chunk_id"])
    return models.PointStruct(
        id=qdrant_point_id(chunk_id),
        vector=chunk.embedding,
        payload=payload,
    )


def index_embedded_chunks(
    client: QdrantClient,
    embedded_chunks: Sequence[EmbeddedChunk],
    collection_name: str = COLLECTION_NAME,
) -> int:
    """Recreate a collection, store all chunks, and return the point count."""
    if not collection_name.strip():
        raise ValueError("collection_name must not be empty.")

    vector_dimension = validate_embedded_chunks(embedded_chunks)
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)

    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=vector_dimension,
            distance=models.Distance.COSINE,
        ),
    )
    client.upsert(
        collection_name=collection_name,
        points=[_point_from_chunk(chunk) for chunk in embedded_chunks],
        wait=True,
    )

    point_count = client.count(collection_name=collection_name, exact=True).count
    if point_count != len(embedded_chunks):
        raise RuntimeError(
            f"Qdrant stored {point_count} points, expected {len(embedded_chunks)}."
        )
    return point_count


def run_indexing_pipeline(
    storage_path: Path = DEFAULT_QDRANT_PATH,
    qdrant_url: str | None = None,
    collection_name: str = COLLECTION_NAME,
    batch_size: int = BATCH_SIZE,
    model_name: str = MODEL_NAME,
) -> IndexingRun:
    """Embed the knowledge base and replace a local or server collection."""
    started_at = perf_counter()
    embedding_run = run_embedding_pipeline(
        batch_size=batch_size,
        model_name=model_name,
    )

    if qdrant_url:
        storage_location = qdrant_url
        client = QdrantClient(url=qdrant_url)
    else:
        resolved_storage_path = storage_path.resolve()
        resolved_storage_path.mkdir(parents=True, exist_ok=True)
        storage_location = str(resolved_storage_path)
        client = QdrantClient(path=storage_location)
    try:
        point_count = index_embedded_chunks(
            client=client,
            embedded_chunks=embedding_run.embedded_chunks,
            collection_name=collection_name,
        )
    finally:
        client.close()

    return IndexingRun(
        collection_name=collection_name,
        storage_location=storage_location,
        point_count=point_count,
        embedding_dimension=embedding_run.embedding_dimension,
        model_name=embedding_run.model_name,
        device=embedding_run.device,
        elapsed_seconds=perf_counter() - started_at,
    )


def print_indexing_report(run: IndexingRun) -> None:
    """Print a compact report that explains what was persisted."""
    separator = "=" * 53
    print(separator)
    print("Qdrant Indexing Report")
    print(separator)
    print(f"Collection:\n{run.collection_name}")
    print(f"Storage location:\n{run.storage_location}")
    print(f"Points stored:\n{run.point_count}")
    print(f"Embedding dimension:\n{run.embedding_dimension}")
    print(f"Embedding model:\n{run.model_name}")
    print(f"Device:\n{run.device}")
    print(f"Total indexing time:\n{run.elapsed_seconds:.2f} seconds")
    print(separator)


def parse_args(arguments: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line options for local or server-backed indexing."""
    parser = argparse.ArgumentParser(
        description="Embed the knowledge base and store it in Qdrant."
    )
    parser.add_argument(
        "--qdrant-url",
        help=(
            "Qdrant server URL, for example http://localhost:6333. "
            "When omitted, embedded storage at data/qdrant/ is used."
        ),
    )
    return parser.parse_args(arguments)


def main() -> None:
    """Run knowledge-base indexing and print its report."""
    arguments = parse_args()
    run = run_indexing_pipeline(qdrant_url=arguments.qdrant_url)
    print_indexing_report(run)


if __name__ == "__main__":
    main()
