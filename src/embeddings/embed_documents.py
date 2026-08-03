"""Generate and validate local dense embeddings for document chunks.

This module intentionally stops after embedding generation. It does not create
vector-store collections, persist vectors, retrieve documents, or call an LLM.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

# Some restricted Windows networks block Hugging Face's optional Xet transfer
# service. Keep the normal HTTP downloader as a reliable local-model fallback.
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

import numpy as np
import torch
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer

if __package__:
    from ..ingestion.load_documents import load_documents
    from ..ingestion.split_documents import split_documents
else:
    # Allow this file to be run directly by VS Code Code Runner.
    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))
    from src.ingestion.load_documents import load_documents
    from src.ingestion.split_documents import split_documents

MODEL_NAME = "BAAI/bge-small-en-v1.5"
BATCH_SIZE = 32
EMBEDDING_PREVIEW_LENGTH = 8


@dataclass(frozen=True)
class EmbeddedChunk:
    """A chunk with its text, preserved metadata, and dense embedding vector.

    The object is deliberately shaped for the future indexing stage, which can
    use ``text``, ``metadata``, and ``embedding`` without transforming it.
    """

    text: str
    metadata: dict[str, object]
    embedding: list[float]


@dataclass(frozen=True)
class EmbeddingRun:
    """The validated output and measurements from one embedding run."""

    embedded_chunks: list[EmbeddedChunk]
    model_name: str
    device: str
    embedding_dimension: int
    average_embedding_norm: float
    elapsed_seconds: float


def select_device() -> str:
    """Return ``cuda`` when PyTorch can use it, otherwise return ``cpu``."""
    return "cuda" if torch.cuda.is_available() else "cpu"


def load_embedding_model(
    model_name: str = MODEL_NAME,
    device: str | None = None,
) -> SentenceTransformer:
    """Load the configured Sentence Transformers model on the selected device."""
    selected_device = device or select_device()
    try:
        return SentenceTransformer(model_name, device=selected_device)
    except Exception as exc:
        raise RuntimeError(
            f"Could not load embedding model '{model_name}'. On the first run, "
            "ensure the machine can reach huggingface.co so the model can be "
            "downloaded and cached locally."
        ) from exc


def validate_chunks(chunks: Sequence[Document]) -> None:
    """Ensure that every input item is a non-empty LangChain document."""
    if not chunks:
        raise ValueError("Cannot generate embeddings for an empty chunk collection.")

    for index, chunk in enumerate(chunks):
        if not isinstance(chunk, Document):
            raise TypeError(f"chunks[{index}] must be a LangChain Document object.")
        if not chunk.page_content.strip():
            raise ValueError(f"chunks[{index}] has empty page_content.")


def validate_embedding_matrix(
    embeddings: np.ndarray,
    expected_count: int,
) -> int:
    """Validate a dense embedding matrix and return its vector dimension."""
    if embeddings.ndim != 2:
        raise ValueError(
            "Embeddings must be a two-dimensional matrix of shape "
            "(chunk_count, embedding_dimension)."
        )
    if embeddings.shape[0] != expected_count:
        raise ValueError(
            f"Embedding count ({embeddings.shape[0]}) does not match chunk count "
            f"({expected_count})."
        )
    if embeddings.shape[1] == 0:
        raise ValueError("Embedding vectors must have at least one dimension.")
    if not np.isfinite(embeddings).all():
        raise ValueError("Embeddings contain NaN or infinite values.")

    return int(embeddings.shape[1])


def embed_chunks(
    chunks: Sequence[Document],
    model: SentenceTransformer,
    batch_size: int = BATCH_SIZE,
) -> list[EmbeddedChunk]:
    """Embed chunks in batches, preserving their order and metadata.

    Args:
        chunks: Retrieval-ready chunks produced by ``split_documents``.
        model: A loaded local Sentence Transformers embedding model.
        batch_size: Number of chunks processed per model batch.
    """
    validate_chunks(chunks)
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero.")

    chunk_texts = [chunk.page_content for chunk in chunks]
    embeddings = np.asarray(
        model.encode(
            chunk_texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=False,
        ),
        dtype=np.float32,
    )
    validate_embedding_matrix(embeddings, expected_count=len(chunks))

    return [
        EmbeddedChunk(
            text=chunk.page_content,
            metadata=dict(chunk.metadata),
            embedding=embedding.astype(float).tolist(),
        )
        for chunk, embedding in zip(chunks, embeddings, strict=True)
    ]


def run_embedding_pipeline(
    batch_size: int = BATCH_SIZE,
    model_name: str = MODEL_NAME,
) -> EmbeddingRun:
    """Load chunks, generate validated embeddings, and return run measurements."""
    chunks = split_documents(load_documents())
    device = select_device()

    started_at = perf_counter()
    model = load_embedding_model(model_name=model_name, device=device)
    embedded_chunks = embed_chunks(chunks, model=model, batch_size=batch_size)
    elapsed_seconds = perf_counter() - started_at

    embedding_matrix = np.asarray(
        [embedded_chunk.embedding for embedded_chunk in embedded_chunks],
        dtype=np.float32,
    )
    embedding_dimension = validate_embedding_matrix(
        embedding_matrix,
        expected_count=len(chunks),
    )
    average_embedding_norm = float(np.linalg.norm(embedding_matrix, axis=1).mean())

    return EmbeddingRun(
        embedded_chunks=embedded_chunks,
        model_name=model_name,
        device=device,
        embedding_dimension=embedding_dimension,
        average_embedding_norm=average_embedding_norm,
        elapsed_seconds=elapsed_seconds,
    )


def print_embedding_report(run: EmbeddingRun) -> None:
    """Print a concise, manual verification report for an embedding run."""
    first_embedding = run.embedded_chunks[0].embedding
    preview = ", ".join(
        f"{value:.4f}" for value in first_embedding[:EMBEDDING_PREVIEW_LENGTH]
    )
    separator = "=" * 53

    print(separator)
    print("Embedding Report")
    print(separator)
    print(f"Embedding model:\n{run.model_name}")
    print(f"Device:\n{run.device}")
    print(f"Chunks processed:\n{len(run.embedded_chunks)}")
    print(f"Embedding dimension:\n{run.embedding_dimension}")
    print(f"Average embedding norm:\n{run.average_embedding_norm:.4f}")
    print(f"Embedding generation time:\n{run.elapsed_seconds:.2f} seconds")
    print(separator)
    print("First embedding:")
    print(f"[{preview}, ...]")
    print(separator)


def main() -> None:
    """Execute the embedding stage and print its verification report."""
    run = run_embedding_pipeline()
    print_embedding_report(run)


if __name__ == "__main__":
    main()
