"""FastAPI API for the local RAG support copilot."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from time import perf_counter
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient

from src.generation.generator import (
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OLLAMA_URL,
)
from src.ingestion.index_documents import COLLECTION_NAME, run_indexing_pipeline
from src.rag import RagResponse, answer_question
from src.retrieval.retriever import DEFAULT_QDRANT_URL, DEFAULT_TOP_K, RetrievedChunk
from src.routing.router import _router_adapter_dir, _router_enabled

QDRANT_URL = os.getenv("QDRANT_URL", DEFAULT_QDRANT_URL)
OLLAMA_URL = os.getenv("OLLAMA_URL", DEFAULT_OLLAMA_URL)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
AUTO_INDEX_ON_START = os.getenv("AUTO_INDEX_ON_START", "false").lower() == "true"


class ChatRequest(BaseModel):
    """Request body for a support chat turn."""

    message: str = Field(..., min_length=1)
    top_k: int = Field(default=DEFAULT_TOP_K, ge=1, le=10)
    debug: bool = False


class RetrievedChunkResponse(BaseModel):
    """Public-safe retrieved evidence returned to the UI."""

    text: str
    source: str
    chunk_id: str
    score: float
    section: str | None = None


class ChatResponse(BaseModel):
    """Response body for a support chat turn."""

    answer: str
    route: str
    needs_handoff: bool
    handoff_reason: str | None = None
    model: str
    routing_backend: str
    elapsed_seconds: float
    sources: list[str] | None = None
    retrieved_chunks: list[RetrievedChunkResponse] | None = None


class ComponentHealth(BaseModel):
    """Health state for one dependency."""

    ok: bool
    detail: str


class HealthResponse(BaseModel):
    """Health response for the API and its local dependencies."""

    backend: ComponentHealth
    qdrant: ComponentHealth
    ollama: ComponentHealth
    model: str
    router: ComponentHealth


def _section(metadata: dict[str, Any]) -> str | None:
    """Return the most specific heading available for a retrieved chunk."""
    section = (
        metadata.get("header_3")
        or metadata.get("header_2")
        or metadata.get("header_1")
    )
    return section if isinstance(section, str) else None


def chunk_response(chunk: RetrievedChunk) -> RetrievedChunkResponse:
    """Convert an internal retrieved chunk to an API response object."""
    return RetrievedChunkResponse(
        text=chunk.text,
        source=str(chunk.metadata.get("source", "unknown-source")),
        chunk_id=str(chunk.metadata.get("chunk_id", "unknown-chunk")),
        score=chunk.score,
        section=_section(chunk.metadata),
    )


def ensure_qdrant_index() -> None:
    """Index knowledge chunks when the configured Qdrant collection is absent."""
    client = QdrantClient(url=QDRANT_URL)
    try:
        has_collection = client.collection_exists(COLLECTION_NAME)
        point_count = 0
        if has_collection:
            point_count = client.count(
                collection_name=COLLECTION_NAME,
                exact=True,
            ).count
    finally:
        client.close()

    if not has_collection or point_count == 0:
        run_indexing_pipeline(qdrant_url=QDRANT_URL)


def check_qdrant() -> ComponentHealth:
    """Check that Qdrant is reachable and report collection point count."""
    try:
        client = QdrantClient(url=QDRANT_URL)
        try:
            if not client.collection_exists(COLLECTION_NAME):
                return ComponentHealth(ok=False, detail="knowledge_chunks missing")
            count = client.count(collection_name=COLLECTION_NAME, exact=True).count
            return ComponentHealth(ok=True, detail=f"{count} indexed chunks")
        finally:
            client.close()
    except Exception as exc:  # noqa: BLE001
        return ComponentHealth(ok=False, detail=str(exc))


def check_ollama() -> ComponentHealth:
    """Check that Ollama is reachable and the configured model is installed."""
    try:
        response = requests.get(
            f"{OLLAMA_URL.rstrip('/')}/api/tags",
            timeout=10,
        )
        response.raise_for_status()
        models = response.json().get("models", [])
        model_names = {
            model.get("name")
            for model in models
            if isinstance(model, dict) and isinstance(model.get("name"), str)
        }
        if OLLAMA_MODEL not in model_names:
            return ComponentHealth(
                ok=False,
                detail=f"{OLLAMA_MODEL} not found in Ollama models",
            )
        return ComponentHealth(ok=True, detail=f"{OLLAMA_MODEL} available")
    except Exception as exc:  # noqa: BLE001
        return ComponentHealth(ok=False, detail=str(exc))


def check_router() -> ComponentHealth:
    """Report configured router mode and adapter availability."""
    if not _router_enabled():
        return ComponentHealth(ok=True, detail="fine-tuned router disabled; using rules")
    adapter_dir = _router_adapter_dir()
    if adapter_dir.exists():
        return ComponentHealth(ok=True, detail=f"fine-tuned router ready at {adapter_dir}")
    return ComponentHealth(ok=False, detail=f"adapter missing at {adapter_dir}")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize the vector index when requested by the container config."""
    if AUTO_INDEX_ON_START:
        ensure_qdrant_index()
    yield


app = FastAPI(
    title="Embeds Support Copilot API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return backend and dependency health."""
    return HealthResponse(
        backend=ComponentHealth(ok=True, detail="running"),
        qdrant=check_qdrant(),
        ollama=check_ollama(),
        model=OLLAMA_MODEL,
        router=check_router(),
    )


@app.post(
    "/api/v1/support/chat",
    response_model=ChatResponse,
    response_model_exclude_none=True,
)
def support_chat(request: ChatRequest) -> ChatResponse:
    """Answer one support question with local RAG."""
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="message must not be empty")

    started_at = perf_counter()
    try:
        response: RagResponse = answer_question(
            question=message,
            qdrant_url=QDRANT_URL,
            top_k=request.top_k,
            ollama_model=OLLAMA_MODEL,
            ollama_url=OLLAMA_URL,
        )
    except requests.exceptions.ConnectionError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Ollama is not reachable. Start Ollama on the host and ensure "
                f"{OLLAMA_URL} is accessible from Docker."
            ),
        ) from exc
    except requests.exceptions.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama returned an error: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    payload = ChatResponse(
        answer=response.answer.answer,
        route=response.route,
        needs_handoff=response.needs_handoff,
        handoff_reason=response.handoff_reason,
        model=response.answer.model,
        routing_backend=response.routing_backend,
        elapsed_seconds=perf_counter() - started_at,
    )
    if request.debug:
        payload.sources = response.answer.sources
        payload.retrieved_chunks = [
            chunk_response(chunk) for chunk in response.retrieved_chunks
        ]
    return payload
