# Target Architecture

> Practice assumptions created for this learning project. These are not final business policies or legal terms.

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

## Components

- Next.js support interface: Future web UI for chat, source display, and support-agent review.
- FastAPI backend: Future API layer for chat, documents, evaluations, health, and escalations.
- LangGraph orchestration: Future state machine that decides whether to retrieve, call a tool, ask for more information, or escalate.
- LangChain retrieval and tools: Future integrations for document retrieval, prompt templates, structured outputs, and tool wrappers.
- Qdrant: Future vector database for knowledge chunks.
- PostgreSQL: Future transactional database for bookings, payments, notifications, tickets, conversations, and audit records.
- General LLM: Main model for natural-language answering.
- QLoRA routing model: Optional fine-tuned adapter for classification, extraction, routing, and formatting.

## Overall Architecture

```mermaid
flowchart TD
  UI[Next.js support interface] --> API[FastAPI backend]
  API --> Graph[LangGraph orchestration]
  Graph --> RAG[LangChain retriever]
  Graph --> Tools[Read-only structured tools]
  RAG --> Qdrant[(Qdrant knowledge chunks)]
  Tools --> Postgres[(PostgreSQL transactional data)]
  Graph --> LLM[General LLM]
  Graph --> Router[Optional QLoRA routing model]
  Graph --> Trace[Evaluation and tracing]
```

## Support-Question Lifecycle

```mermaid
sequenceDiagram
  participant U as User
  participant API as FastAPI
  participant G as LangGraph
  participant R as Retriever
  participant T as Tools
  participant M as LLM
  U->>API: Ask support question
  API->>G: Create graph state
  G->>G: Classify and extract entities
  alt Policy question
    G->>R: Retrieve documents
    R-->>G: Evidence chunks
  else Transactional question
    G->>T: Call read-only tool
    T-->>G: Current record
  end
  G->>M: Generate grounded response
  M-->>G: Answer
  G-->>API: Answer, sources, trace summary
  API-->>U: Response
```

## Document-Ingestion Lifecycle

```mermaid
flowchart LR
  A[Markdown file] --> B[Load document]
  B --> C[Normalize text]
  C --> D[Preserve headings]
  D --> E[Chunk]
  E --> F[Attach metadata]
  F --> G[Embed chunks]
  G --> H[Store in Qdrant]
  H --> I[Run retrieval tests]
```

## Evaluation Lifecycle

```mermaid
flowchart TD
  Cases[Evaluation cases] --> Run[Run system]
  Run --> Metrics[Calculate metrics]
  Metrics --> Review[Human review]
  Review --> Log[Experiment log]
  Log --> Decision{Promote change?}
  Decision -->|Yes| Version[Record versions]
  Decision -->|No| Iterate[Change retriever, prompt, or data]
```

## Fine-Tuning Lifecycle

```mermaid
flowchart LR
  A[Reviewed examples] --> B[Label validation]
  B --> C[Train/validation/test split]
  C --> D[QLoRA adapter training]
  D --> E[Behavior evaluation]
  E --> F[Compare with base model]
  F --> G[Save adapter if useful]
```

## Key Differences

- Offline indexing: Loading, chunking, embedding, and storing documents before user questions arrive.
- Online retrieval: Searching Qdrant at question time.
- Online generation: Creating the answer from current user input and evidence.
- Tool execution: Reading current transactional records from databases or APIs.
- Model training: Updating adapter weights from reviewed behavior examples.

