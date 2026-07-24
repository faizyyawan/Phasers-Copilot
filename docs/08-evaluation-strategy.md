# Evaluation Strategy

Evaluation turns RAG development from guesswork into measurable learning.

## Retrieval Metrics

- Recall@1: Whether the expected source appears in the top 1.
- Recall@3: Whether the expected source appears in the top 3.
- Recall@5: Whether the expected source appears in the top 5.
- Precision@K: How many retrieved chunks are relevant.
- Mean Reciprocal Rank: How high the first relevant result appears.
- nDCG: Ranking quality when relevance has grades.
- Metadata-filter accuracy: Whether filters include allowed documents and exclude disallowed ones.
- Retrieval latency: Time to return results.

## Generation Metrics

- Correctness
- Groundedness
- Citation accuracy
- Completeness
- Relevance
- Refusal accuracy
- Hallucination rate

## Routing and Agent Metrics

- Intent-classification accuracy
- Entity-extraction accuracy
- Tool-selection accuracy
- Routing accuracy
- Escalation accuracy
- Unnecessary retrieval rate
- Unnecessary tool-call rate
- Average graph steps
- Graph-node failure rate

## Test Sets

- Development test set: Used frequently while building.
- Validation set: Used to compare approaches after development tuning.
- Held-out test set: Used rarely to estimate true performance.
- Regression tests: Re-run after each change.

Avoid test leakage by not training prompts, rerankers, or adapters on held-out examples.

## Human and Automated Evaluation

Automated metrics catch regressions quickly. Human evaluation is needed for nuance, tone, escalation judgment, and source usefulness.

LLM-as-judge can help scale review, but it may be biased, inconsistent, or too forgiving. Keep judge prompts versioned and compare with human labels.

## Initial Learning Targets

These are learning targets, not production guarantees:

- At least 80% Recall@3 on the first controlled dataset.
- Correct refusal for unsupported policy questions.
- No guaranteed refunds or cancellations.
- Correct source attribution.
- Correct routing between RAG and structured tools.

