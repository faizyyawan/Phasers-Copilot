# Development Roadmap

## Phase 1: Foundations and Baseline RAG

### Week 1

- Learning objectives: LLM fundamentals, embeddings, structured output, project setup.
- Reading topics: tokens, prompts, context windows, hallucinations.
- Concepts: temperature, JSON output, source grounding.
- Features to implement yourself: project environment and first prompt experiments.
- Deliverables: notes in [19-learning-journal-template.md](19-learning-journal-template.md).
- Acceptance criteria: You can explain RAG vs tools vs QLoRA.
- Suggested tests: Ask the model unsupported policy questions.
- Common beginner mistakes: Treating the model as a database.
- Difficulty: Easy.
- Reflection: What kinds of answers should never rely on memory?

### Week 2

- Learning objectives: Knowledge documents and ingestion design.
- Reading topics: Markdown loading, metadata, chunking.
- Concepts: document IDs, chunk IDs, versions.
- Features to implement yourself: Markdown loader plan and manual corpus review.
- Deliverables: First ingestion design notes.
- Acceptance criteria: Every document has metadata.
- Suggested tests: Verify title, category, and version extraction.
- Common beginner mistakes: Losing headings during chunking.
- Difficulty: Easy-medium.
- Reflection: Which chunks are understandable without surrounding text?

### Week 3

- Learning objectives: Basic retrieval and grounded FastAPI endpoint.
- Reading topics: vector search, Qdrant basics, citations.
- Concepts: embeddings, semantic similarity, context construction.
- Features to implement yourself: dense retriever and basic chat endpoint.
- Deliverables: Basic RAG MVP.
- Acceptance criteria: 80% Recall@3 on easy development cases.
- Suggested tests: Run retrieval and answer cases.
- Common beginner mistakes: Returning answers without sources.
- Difficulty: Medium.
- Reflection: Which failures were retrieval failures versus generation failures?

## Phase 2: Advanced Retrieval

### Week 4

- Learning objectives: Chunking experiments.
- Reading topics: chunk size, overlap, heading-aware splitting.
- Concepts: parent context, metadata, reindexing.
- Features to implement yourself: configurable chunking.
- Deliverables: Experiment log comparing chunk sizes.
- Acceptance criteria: Best setting chosen by metrics.
- Suggested tests: Retrieval cases across easy and ambiguous questions.
- Common beginner mistakes: Assuming bigger chunks are always better.
- Difficulty: Medium.
- Reflection: What changed when chunk overlap changed?

### Week 5

- Learning objectives: Sparse and hybrid retrieval.
- Reading topics: BM25, hybrid search, RRF.
- Concepts: exact terms, status names, keyword matching.
- Features to implement yourself: BM25 and fusion.
- Deliverables: Dense vs sparse vs hybrid comparison.
- Acceptance criteria: Hybrid preserves or improves Recall@3.
- Suggested tests: Typo and exact-status cases.
- Common beginner mistakes: Combining raw dense and sparse scores directly.
- Difficulty: Medium.
- Reflection: Which queries needed keywords more than embeddings?

### Week 6

- Learning objectives: Reranking and query transformation.
- Reading topics: rerankers, query rewriting, decomposition.
- Concepts: MRR, nDCG, latency tradeoffs.
- Features to implement yourself: reranker experiment and rewrite step.
- Deliverables: Reranking report.
- Acceptance criteria: MRR improves on validation data.
- Suggested tests: Ambiguous and multi-document questions.
- Common beginner mistakes: Rewriting away user intent.
- Difficulty: Medium-hard.
- Reflection: Did improved ranking justify extra latency?

## Phase 3: Evaluation

### Week 7

- Learning objectives: Retrieval, generation, and refusal evaluation.
- Reading topics: groundedness, LLM-as-judge limitations, regression tests.
- Concepts: dev/validation/test splits, leakage.
- Features to implement yourself: evaluation harness.
- Deliverables: First evaluation dashboard or report.
- Acceptance criteria: Metrics are reproducible.
- Suggested tests: Retrieval, answer, routing, adversarial datasets.
- Common beginner mistakes: Tuning on the held-out set.
- Difficulty: Medium-hard.
- Reflection: Which metric best predicted answer quality?

## Phase 4: LangGraph

### Week 8

- Learning objectives: State, nodes, edges, basic workflow.
- Reading topics: LangGraph state and conditional edges.
- Concepts: graph state, route decisions.
- Features to implement yourself: basic RAG graph.
- Deliverables: Graph with classify, retrieve, answer.
- Acceptance criteria: Node outputs are testable.
- Suggested tests: Graph route unit tests.
- Common beginner mistakes: Putting all logic in one node.
- Difficulty: Medium.
- Reflection: What state fields were actually necessary?

### Week 9

- Learning objectives: Corrective RAG, evidence grading, retries, routing.
- Reading topics: evidence grading, recovery loops.
- Concepts: max retries, low-confidence paths.
- Features to implement yourself: evidence grading and retry once.
- Deliverables: Corrective RAG experiment.
- Acceptance criteria: Weak evidence does not produce confident answers.
- Suggested tests: Unanswerable and ambiguous questions.
- Common beginner mistakes: Infinite loops.
- Difficulty: Hard.
- Reflection: When should the system ask a question instead of retrying?

### Week 10

- Learning objectives: Structured booking, payment, and notification tools.
- Reading topics: tool schemas, validation, authorization.
- Concepts: read-only tools, transactional data.
- Features to implement yourself: mock-backed lookup tools.
- Deliverables: Tool route integration.
- Acceptance criteria: Booking status questions use tools.
- Suggested tests: Routing and unauthorized cases.
- Common beginner mistakes: Embedding current records in RAG.
- Difficulty: Hard.
- Reflection: Which questions looked like policy questions but needed tools?

### Week 11

- Learning objectives: Persistence, checkpoints, memory, human escalation.
- Reading topics: graph persistence and audit trails.
- Concepts: checkpointing, human-in-the-loop.
- Features to implement yourself: saved graph state and escalation records.
- Deliverables: Escalation workflow.
- Acceptance criteria: Disputes produce a human-review summary.
- Suggested tests: Refund dispute and privacy cases.
- Common beginner mistakes: Saving sensitive traces without redaction.
- Difficulty: Hard.
- Reflection: What should be stored, and what should be redacted?

## Phase 5: QLoRA

### Week 12

- Learning objectives: Dataset design and preparation.
- Reading topics: LoRA, QLoRA, labels, data splits.
- Concepts: behavior data versus policy facts.
- Features to implement yourself: reviewed training dataset.
- Deliverables: Label schema and split plan.
- Acceptance criteria: No changing policy facts in labels.
- Suggested tests: JSONL validation and label audit.
- Common beginner mistakes: Training the model to memorize refund policy.
- Difficulty: Medium-hard.
- Reflection: What behavior should the adapter learn?

### Week 13

- Learning objectives: QLoRA training experiments.
- Reading topics: PEFT, TRL, bitsandbytes, NF4.
- Concepts: adapters, quantization, checkpoints.
- Features to implement yourself: small adapter training run.
- Deliverables: Training log and saved adapter.
- Acceptance criteria: Training completes and validation is recorded.
- Suggested tests: Valid JSON rate before/after.
- Common beginner mistakes: Ignoring tokenizer chat template.
- Difficulty: Hard.
- Reflection: Did training improve behavior or only imitate examples?

### Week 14

- Learning objectives: Model evaluation and integration.
- Reading topics: adapter evaluation and regression testing.
- Concepts: base vs adapter comparison.
- Features to implement yourself: adapter evaluation harness.
- Deliverables: Decision report.
- Acceptance criteria: Adapter improves selected behavior metric.
- Suggested tests: Held-out routing cases.
- Common beginner mistakes: Shipping an adapter with worse refusal behavior.
- Difficulty: Hard.
- Reflection: Would prompt changes have solved the same problem?

## Phase 6: Productization

### Week 15

- Learning objectives: FastAPI backend completion and Next.js interface.
- Reading topics: streaming, auth, UI source display.
- Concepts: API contracts, idempotency, trace summaries.
- Features to implement yourself: full backend and frontend flow.
- Deliverables: Usable support interface.
- Acceptance criteria: Users see answers, sources, and escalation states.
- Suggested tests: API and end-to-end tests.
- Common beginner mistakes: Exposing raw internal traces.
- Difficulty: Hard.
- Reflection: What information does a user need versus an admin?

### Week 16

- Learning objectives: Deployment, observability, security review, final evaluation.
- Reading topics: Docker Compose, monitoring, secrets, backups.
- Concepts: operational readiness.
- Features to implement yourself: deployable local/staging environment.
- Deliverables: Final evaluation and security checklist.
- Acceptance criteria: Full definition of done is met.
- Suggested tests: Regression, adversarial, load smoke tests.
- Common beginner mistakes: Treating deployment as only container startup.
- Difficulty: Hard.
- Reflection: What would fail first with real users?

