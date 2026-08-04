# Definition of Done

## Basic RAG MVP

- Markdown knowledge documents are loaded.
- Chunks include metadata and source file names.
- Dense retrieval returns relevant documents.
- Answers are grounded in retrieved chunks.
- Customer-facing answers hide source files and chunks by default.
- Debug traces expose sources and chunks only when explicitly requested.
- Unsupported questions are refused.
- Basic retrieval and answer tests pass.

## Advanced Retrieval

- Metadata filtering works.
- Sparse retrieval is evaluated.
- Hybrid retrieval is evaluated.
- Reranking is evaluated.
- Query rewriting or decomposition is tested.
- Metrics show the chosen approach improves or preserves quality.

## LangGraph Agent

- State schema is clear and tested.
- Nodes have narrow responsibilities.
- Conditional routing works.
- Retry limits prevent loops.
- Low-confidence and sensitive cases escalate.
- Checkpoints support debugging.

## Structured Tools

- Tools are read-only.
- Inputs are validated.
- Authorization is enforced.
- Tool failures do not produce fabricated answers.
- Exact booking/payment/notification questions route to tools.

## QLoRA Experiment

- Dataset is reviewed and split.
- Label schema is versioned.
- Adapter is trained on behavior tasks only.
- Base model and adapter are compared.
- Refusal behavior does not regress.
- Results are recorded in an experiment log.

## Full Project

- RAG, tools, LangGraph, evaluation, UI, backend, persistence, security, and observability work together.
- The system keeps policy answers grounded and exposes source traces only in debug/admin views.
- The system uses tools for current transactional answers.
- The system escalates uncertain or sensitive cases.
- Final evaluation results are documented.
- Practice-policy limitations are clear.
