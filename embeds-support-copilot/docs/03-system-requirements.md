# System Requirements

All targets in this file are initial learning targets, not guaranteed production standards.

## Functional Requirements

- FR-001: The system shall answer support questions using retrieved knowledge documents.
- FR-002: The system shall cite source documents used for policy answers.
- FR-003: The system shall refuse unsupported policy claims.
- FR-004: The system shall identify when a question requires current booking data.
- FR-005: The system shall use read-only structured tools for booking, payment, notification, availability, and ticket lookups.
- FR-006: The system shall escalate disputes, low-confidence answers, privacy-sensitive requests, and refund guarantees.
- FR-007: The system shall preserve conversation context for follow-up questions.
- FR-008: The system shall support evaluation runs over controlled datasets.

## Non-Functional Requirements

- NFR-001: The MVP should keep local development setup understandable for a beginner.
- NFR-002: The first RAG endpoint should target under 5 seconds latency on a local learning dataset.
- NFR-003: Retrieval configuration should be versioned in experiment logs.
- NFR-004: Prompts should be versioned and regression tested.
- NFR-005: Failures should produce safe user-facing messages.

## Security Requirements

- SEC-001: Tools must be allow-listed.
- SEC-002: The first version must not execute unrestricted SQL.
- SEC-003: The first version must not modify bookings, payments, refunds, or availability.
- SEC-004: Users must only access records they are authorized to view.
- SEC-005: Prompt-injection attempts in user input or documents must not override system rules.
- SEC-006: Secrets must be stored outside source control.

## Privacy Requirements

- PRIV-001: Personal data in traces should be minimized or redacted.
- PRIV-002: Support answers should not reveal another customer's records.
- PRIV-003: Evaluation datasets should use fake data only.
- PRIV-004: Retention policies should be documented before production use.

## Evaluation Requirements

- EVAL-001: Retrieval tests shall measure Recall@1, Recall@3, Recall@5, MRR, and latency.
- EVAL-002: Answer tests shall measure correctness, groundedness, citation accuracy, and refusal accuracy.
- EVAL-003: Routing tests shall measure tool-selection and escalation accuracy.
- EVAL-004: Adversarial tests shall include prompt injection and privacy attacks.
- EVAL-005: Test cases shall be split into development, validation, and held-out sets.

## Observability Requirements

- OBS-001: Each answer should log prompt version, retriever version, model version, and source chunks.
- OBS-002: Tool calls should log tool name, validated input, success/failure, and latency.
- OBS-003: Graph runs should log node path, retry count, and final route.
- OBS-004: Sensitive values should be redacted from traces.

## Performance Goals

- PERF-001: MVP retrieval should return top 5 chunks in under 1 second on the small local dataset.
- PERF-002: MVP chat response should complete in under 5 seconds for common questions.
- PERF-003: Advanced retrieval may trade extra latency for better ranking.

## Reliability Goals

- REL-001: Failed retrieval should produce a safe fallback.
- REL-002: Failed tools should not fabricate transactional answers.
- REL-003: Graph retries should stop after configured maximum attempts.
- REL-004: Evaluation regressions should block promotion to the next phase.

## MVP Requirements

- MVP-001: Markdown knowledge documents are loaded and indexed.
- MVP-002: Basic dense retrieval works.
- MVP-003: Grounded answers include citations.
- MVP-004: Unsupported questions are refused.
- MVP-005: Evaluation cases can be run manually or with a simple future harness.

## Final-System Requirements

- FINAL-001: The system routes among RAG, structured tools, no-tool answers, and human escalation.
- FINAL-002: The system supports LangGraph checkpoints and recovery.
- FINAL-003: The system uses structured evaluation before changes are accepted.
- FINAL-004: QLoRA experiments improve behavior metrics without storing policy facts.

