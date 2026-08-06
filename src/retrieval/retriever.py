"""Retrieve relevant knowledge chunks from Qdrant."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from ..embeddings.embed_documents import MODEL_NAME, load_embedding_model
from ..ingestion.index_documents import COLLECTION_NAME, DEFAULT_QDRANT_PATH

DEFAULT_QDRANT_URL = "http://localhost:6333"
DEFAULT_TOP_K = 3


@dataclass(frozen=True)
class RetrievedChunk:
    """A Qdrant match converted into the shape the generator needs."""

    text: str
    metadata: dict[str, Any]
    score: float


def validate_query(question: str) -> None:
    """Reject empty retrieval queries."""
    if not question.strip():
        raise ValueError("question must not be empty.")


def validate_top_k(top_k: int) -> None:
    """Reject invalid retrieval limits."""
    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")


def embed_query(question: str, model: SentenceTransformer) -> list[float]:
    """Embed one user question with the same model used for document indexing."""
    validate_query(question)
    embedding = np.asarray(
        model.encode(
            [question],
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=False,
        ),
        dtype=np.float32,
    )
    if embedding.ndim != 2 or embedding.shape[0] != 1 or embedding.shape[1] == 0:
        raise ValueError("Query embedding must have shape (1, embedding_dimension).")
    if not np.isfinite(embedding).all():
        raise ValueError("Query embedding contains NaN or infinite values.")
    return embedding[0].astype(float).tolist()


def _chunk_from_point(point: Any) -> RetrievedChunk:
    """Convert a Qdrant scored point into a RetrievedChunk."""
    payload = dict(point.payload or {})
    text = payload.pop("text", "")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Retrieved point is missing non-empty payload text.")

    return RetrievedChunk(
        text=text,
        metadata=payload,
        score=float(point.score),
    )


def retrieve_chunks(
    question: str,
    client: QdrantClient,
    model: SentenceTransformer,
    collection_name: str = COLLECTION_NAME,
    top_k: int = DEFAULT_TOP_K,
) -> list[RetrievedChunk]:
    """Return the top-k semantically similar chunks for a support question."""
    validate_query(question)
    validate_top_k(top_k)
    query_vector = embed_query(question, model)

    response = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k,
        with_payload=True,
        with_vectors=False,
    )
    return [_chunk_from_point(point) for point in response.points]


def retrieve_from_qdrant(
    question: str,
    qdrant_url: str | None = DEFAULT_QDRANT_URL,
    storage_path: Path = DEFAULT_QDRANT_PATH,
    collection_name: str = COLLECTION_NAME,
    top_k: int = DEFAULT_TOP_K,
    model_name: str = MODEL_NAME,
) -> list[RetrievedChunk]:
    """Load the embedding model and retrieve chunks from server or local Qdrant."""
    model = load_embedding_model(model_name=model_name)
    if qdrant_url:
        client = QdrantClient(url=qdrant_url)
    else:
        client = QdrantClient(path=str(storage_path.resolve()))

    try:
        return retrieve_chunks(
            question=question,
            client=client,
            model=model,
            collection_name=collection_name,
            top_k=top_k,
        )
    finally:
        client.close()


def format_retrieval_report(chunks: Sequence[RetrievedChunk]) -> str:
    """Create a human-readable retrieval report for CLI inspection."""
    lines = ["Retrieved chunks:"]
    if not chunks:
        return "No chunks retrieved."

    for index, chunk in enumerate(chunks, start=1):
        source = chunk.metadata.get("source", "unknown-source")
        chunk_id = chunk.metadata.get("chunk_id", "unknown-chunk")
        section = chunk.metadata.get("header_2") or chunk.metadata.get("header_1")
        preview = " ".join(chunk.text.split())[:220]
        lines.append(f"{index}. {source} / {chunk_id}")
        if section:
            lines.append(f"   Section: {section}")
        lines.append(f"   Score: {chunk.score:.4f}")
        lines.append(f"   Preview: {preview}")
    return "\n".join(lines)


def parse_args(arguments: list[str] | None = None) -> argparse.Namespace:
    """Parse retrieval command-line options."""
    parser = argparse.ArgumentParser(description="Retrieve relevant Qdrant chunks.")
    parser.add_argument("question", help="Support question to search for.")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--qdrant-url", default=DEFAULT_QDRANT_URL)
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use embedded Qdrant storage at data/qdrant instead of localhost.",
    )
    return parser.parse_args(arguments)


def main() -> None:
    """Run dense retrieval and print the matching chunks."""
    arguments = parse_args()
    chunks = retrieve_from_qdrant(
        question=arguments.question,
        qdrant_url=None if arguments.local else arguments.qdrant_url,
        top_k=arguments.top_k,
    )
    print(format_retrieval_report(chunks))


if __name__ == "__main__":
    main()
