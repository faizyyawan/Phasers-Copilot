# Embeds Support Copilot

Embeds Support Copilot is a learning project for building a customer-support chatbot for a fictional sports-court booking platform. The goal is to move step by step from a beginner RAG system to a complete support copilot that uses retrieval, structured tools, LangGraph orchestration, evaluation, and later QLoRA fine-tuning.

> Practice assumptions created for this learning project. These are not final business policies or legal terms.

## Problem Statement

Sports-court booking support requires two different kinds of answers. Some answers come from policies and guides, such as cancellation rules or troubleshooting steps. Other answers require current transactional data, such as the status of booking `BK-1001`. A useful support copilot must know which source to use.

## Intended Users

- Customers who book courts.
- Court owners who manage court listings, slots, and availability.
- Support agents who handle escalations.
- Administrators who monitor quality, safety, and evaluation.

## Core Learning Separation

```text
RAG = changing factual knowledge
Structured tools = current transactional information
QLoRA = behavior, classification, routing, and formatting
```

RAG should answer from documents such as booking policies, payment policies, refund rules, troubleshooting guides, and FAQs.

Structured tools should read current records such as booking status, payment status, notification history, court availability, and previous support tickets.

QLoRA should improve behavior: intent classification, entity extraction, query rewriting, tool selection, escalation decisions, structured JSON output, refusal behavior, and support-response style. It should not store business-policy facts.

## Planned Technology Stack

- Python
- FastAPI
- LangChain
- LangGraph
- Qdrant
- PostgreSQL
- Hugging Face Transformers
- PEFT
- TRL
- QLoRA
- Next.js
- Docker
- LangSmith or an equivalent evaluation platform

## Current Project Status

This repository currently contains documentation, fictional support policies, mock transactional data, evaluation datasets, fine-tuning sample formats, and a Dockerized local support chatbot. Markdown loading, heading-aware chunking, embedding generation, Qdrant indexing, dense retrieval, grounded answer generation, FastAPI, Streamlit UI, rule-based routing, and mock read-only support lookups are implemented and tested.

LangGraph orchestration, PostgreSQL-backed structured tools, richer evaluation dashboards, Next.js production UI, and QLoRA experiments are planned later phases.

## What You Will Build Yourself

- Document ingestion pipeline
- Chunking and embedding pipeline
- Qdrant indexing and retrieval
- FastAPI backend
- LangChain retrievers and tools
- LangGraph workflow
- PostgreSQL schemas and queries
- Evaluation harness
- Next.js support interface
- Docker environment
- QLoRA training experiments

## What This Documentation Provides

- A target architecture and phased roadmap
- Fictional but internally consistent support documents for RAG
- Evaluation cases for retrieval, answers, routing, and adversarial behavior
- Mock JSON records for future read-only structured tools
- Fine-tuning label schema and small reviewed-style JSONL examples

## High-Level Architecture

```text
Next.js support interface
          |
FastAPI backend
          |
LangGraph orchestration
          |
LangChain retrieval and tools
          |
Qdrant + PostgreSQL
          |
General LLM + QLoRA routing model
```

## Project Phases

1. Foundations and baseline RAG
2. Advanced retrieval
3. Evaluation
4. LangGraph orchestration
5. Structured tools
6. QLoRA behavior experiments
7. Productization and deployment planning

## Folder Structure

```text
embeds-support-copilot/
|-- README.md
|-- docs/
|-- knowledge-base/
|-- evaluation-data/
|-- mock-data/
`-- fine-tuning-data/
```

## First Milestone

Build a basic support chatbot MVP that loads Markdown knowledge documents, chunks them, embeds them, stores them in a vector database, retrieves relevant chunks, and generates grounded customer-facing answers. Sources and retrieval chunks are hidden from customers by default and available only through debug traces.

Do not skip directly to LangGraph or QLoRA. A weak baseline RAG system is the foundation you will evaluate and improve.

## How to Use This Repository

Work through the project phase by phase. Start by reading [docs/01-project-overview.md](docs/01-project-overview.md), [docs/02-learning-objectives.md](docs/02-learning-objectives.md), and [docs/16-development-roadmap.md](docs/16-development-roadmap.md). Then use the files in [knowledge-base/](knowledge-base/) as the first RAG corpus.

Implement one capability, evaluate it, record the experiment, and only then move to the next capability. Do not jump to LangGraph, structured tools, or QLoRA before you have a working and evaluated baseline retrieval system.

## Windows Development Environment

### First-time setup

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
```

This requires the 64-bit Python 3.11 launcher entry (`py -3.11`). If it is
missing, install Python 3.11 first, then rerun the command. VS Code is already
configured to use `.venv\Scripts\python.exe`; after setup, use **Python:
Select Interpreter** once and choose that workspace interpreter if VS Code has
not selected it automatically.

The setup script detects an NVIDIA GPU automatically. Without one, it installs
CPU-only PyTorch and completes verification in CPU mode.

### Normal daily use

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

Opening a new terminal requires activating `.venv` again.

If your PowerShell execution policy prevents activation, use the virtual
environment interpreter directly instead:

```powershell
& .\.venv\Scripts\python.exe -m pytest -q
& .\.venv\Scripts\python.exe -m src.ingestion.load_documents
```

### Verify the environment

```powershell
python .\scripts\verify_environment.py
```

### Build the local knowledge index

```powershell
python -m src.ingestion.index_documents
```

This command loads and chunks the Markdown knowledge base, generates embeddings,
and replaces the `knowledge_chunks` collection in `data/qdrant/`. Replacing the
collection prevents stale or duplicate chunks during this learning-stage full
reindex workflow.

### Explore the index in Qdrant Dashboard

Start Docker Desktop, then run:

```powershell
docker compose up -d
python -m src.ingestion.index_documents --qdrant-url http://localhost:6333
```

Open [http://localhost:6333/dashboard](http://localhost:6333/dashboard), select
**Collections**, and open `knowledge_chunks` to inspect its 93 points, vectors,
and payload metadata. The Compose service binds only to localhost and keeps its
database in the named Docker volume `qdrant_storage`.

Stop the server without deleting its data:

```powershell
docker compose down
```

The original command without `--qdrant-url` remains available for lightweight
embedded Qdrant usage without Docker.

### Run the Dockerized test UI

This starts Qdrant, a FastAPI backend, and a Streamlit frontend in separate
containers. Ollama stays on the Windows host and is reached from the backend at
`http://host.docker.internal:11434`.

Start Ollama and confirm the local model exists:

```powershell
ollama serve
ollama list
```

Then start the app stack:

```powershell
docker compose up --build
```

Use `--build` after code changes so Docker picks up the latest backend and
frontend files.

Open [http://localhost:8501](http://localhost:8501) and ask a question such as:

```text
How much advance must I pay?
```

The backend API is available at [http://localhost:8000](http://localhost:8000).
Its health endpoint should report Qdrant chunks and `qwen3:8b` availability:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

### Exit the environment

```powershell
deactivate
```

## Definition of Done

See [docs/20-definition-of-done.md](docs/20-definition-of-done.md). At a high level, the project is done when it can route policy questions to RAG, transactional questions to read-only tools, escalate sensitive or uncertain cases, keep customer answers natural, expose debug traces only when requested, pass evaluation targets, and preserve user privacy.
