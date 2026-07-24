# Retrieval Design

Exact identifiers such as booking IDs, payment references, and phone numbers should not rely only on semantic search. They require structured tools or exact database lookups because embeddings may match similar-looking text incorrectly.

## Level 1: Dense Semantic Retrieval

- Purpose: Retrieve by meaning.
- Inputs: User question, embedded knowledge chunks.
- Outputs: Top-k chunks with scores.
- Implement: Embedding model, vector store, retriever.
- Test: Direct and paraphrased policy questions.
- Common mistakes: Using too-large chunks, ignoring citations.
- Acceptance criteria: Easy policy questions retrieve expected documents in top 3.

## Level 2: Metadata Filtering

- Purpose: Restrict retrieval by category, role, status, or version.
- Inputs: Query, metadata filters.
- Outputs: Filtered ranked chunks.
- Implement: Category filters such as `payments` or `refunds`.
- Test: Compare filtered and unfiltered results.
- Common mistakes: Over-filtering and hiding relevant documents.
- Acceptance criteria: Filtered results contain only allowed active documents.

## Level 3: Sparse Keyword Retrieval

- Purpose: Improve exact term matching.
- Inputs: Query text and chunk text.
- Outputs: Keyword-ranked chunks.
- Implement: BM25 or equivalent sparse search.
- Test: Misspellings, exact policy terms, status names.
- Common mistakes: Assuming keyword search understands meaning.
- Acceptance criteria: Exact status and policy terms rank highly.

## Level 4: Hybrid Retrieval

- Purpose: Combine semantic and keyword strengths.
- Inputs: Dense ranking, sparse ranking.
- Outputs: Fused ranking.
- Implement: Reciprocal Rank Fusion.
- Test: Compare Recall@3 against dense-only.
- Common mistakes: Combining unnormalized scores directly.
- Acceptance criteria: Hybrid retrieval improves or preserves Recall@3.

## Level 5: Reranking

- Purpose: Improve ordering of candidate chunks.
- Inputs: Query and top candidates.
- Outputs: Reranked candidates.
- Implement: Cross-encoder or LLM reranker experiment.
- Test: MRR and nDCG before/after.
- Common mistakes: Reranking too many chunks and increasing latency.
- Acceptance criteria: Top result quality improves on validation set.

## Level 6: Query Rewriting and Decomposition

- Purpose: Improve vague, follow-up, or multi-part questions.
- Inputs: Conversation history and current question.
- Outputs: Rewritten query or subqueries.
- Implement: Structured query rewrite output.
- Test: Follow-up questions and multi-document cases.
- Common mistakes: Rewriting away important user details.
- Acceptance criteria: Rewritten queries improve retrieval without fabricating facts.

