# Document-Ingestion Design

## Supported Formats

- Initial format: Markdown
- Future formats: PDF, HTML, JSON, DOCX

## Pipeline Responsibilities

1. Load documents from [../knowledge-base/](../knowledge-base/).
2. Normalize text while preserving important headings.
3. Split into chunks.
4. Attach metadata.
5. Create stable document IDs and chunk IDs.
6. Embed chunks.
7. Store vectors and metadata.
8. Reindex changed documents.
9. Delete outdated inactive chunks.

## Text Normalization

Normalize line endings, remove duplicate whitespace, preserve headings, preserve lists, and avoid deleting policy qualifiers such as "may qualify" or "must not guarantee."

## Chunking

Recommended experimental starting values:

```text
Chunk size: 400-700 tokens
Chunk overlap: 50-100 tokens
```

These are learning starting points, not optimal defaults. Test them against retrieval cases before deciding.

## Metadata

Proposed metadata:

```json
{
  "document_id": "payment-policy-v1",
  "chunk_id": "payment-policy-v1-section-3-chunk-1",
  "title": "Payment Policy",
  "section": "Payment verification",
  "category": "payments",
  "version": "1.0",
  "status": "active",
  "source": "payment-policy.md"
}
```

## Versioning

Each knowledge document should have a document ID and version. Updating policy content should create a new version or mark previous chunks inactive.

## Deduplication

Detect duplicate chunks by content hash. Avoid storing repeated boilerplate as separate high-ranking chunks if it hurts retrieval.

## Reindexing

Reindex when a file changes, an embedding model changes, chunk settings change, or metadata schema changes.

## Deleting Outdated Documents

Do not silently leave stale policy chunks active. Mark old chunks inactive or delete them during reindexing.

## Future Implementation Tasks

- Implement a Markdown loader.
- Implement heading-aware chunking.
- Generate stable IDs.
- Store metadata beside vectors.
- Build a reindex command.
- Write ingestion tests.

