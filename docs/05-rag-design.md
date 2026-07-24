# RAG Design

## What RAG Is

Retrieval-Augmented Generation, or RAG, combines document retrieval with LLM generation. The system first finds relevant knowledge chunks, then asks the model to answer using that evidence.

## Why This Project Needs RAG

Support policies change. Booking, payment, cancellation, refund, notification, and troubleshooting information should be updated as documents rather than memorized inside a model.

## What Belongs in RAG

- Booking policies
- Payment policies
- Cancellation policies
- Refund rules
- Troubleshooting guides
- Court-owner instructions
- Notification instructions
- Frequently asked questions

## What Does Not Belong in RAG

- Current booking status
- Current payment status
- Notification history
- Customer-specific tickets
- Secrets
- Private user data
- Instructions that override system behavior

## Basic First-Version Pipeline

```text
Question
  |
Retrieve top relevant chunks
  |
Build grounded prompt
  |
Generate answer
  |
Return answer and sources
```

## Advanced Target Pipeline

Later phase only:

```text
Question
  |
Classify and rewrite
  |
Dense + sparse retrieval
  |
Fusion
  |
Reranking
  |
Evidence grading
  |
Grounded generation
  |
Groundedness verification
```

## Document Lifecycle

Documents begin as Markdown files in [../knowledge-base/](../knowledge-base/). A future ingestion process should load them, assign document IDs, preserve headings, split them into chunks, embed each chunk, and store active chunks in Qdrant.

## Chunk Lifecycle

Chunks should preserve enough context to answer a question. Each chunk should include metadata such as title, section, category, version, source file, and active status.

## Embedding Lifecycle

When a document changes, affected chunks should be re-embedded. Store the embedding model name and document version so evaluation results can be compared fairly.

## Retrieval Lifecycle

The initial retriever should return top-k semantically similar chunks. Later versions can add metadata filtering, BM25, hybrid search, reranking, and query rewriting.

## Context Construction

The prompt should include only relevant evidence, source labels, and clear instructions to answer from the evidence. Avoid dumping entire documents into the prompt.

## Answer Generation

Answers should be short, helpful, and grounded. If the answer requires a booking, payment, notification, or ticket lookup, the system should route to a structured tool instead of guessing.

## Citation Generation

Each factual policy answer should cite source file names or document IDs. Citation accuracy should be evaluated separately from answer correctness.

## Refusal Behavior

The assistant should refuse to guarantee refunds, cancellations, legal rights, or private information not supported by evidence and authorization.

