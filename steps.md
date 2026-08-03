# Next Steps

This file is the working checklist for moving the project from the current local RAG foundation toward a tested support copilot. Each step includes what to build and how to confirm it works.

## Current Baseline

The repository already contains:

- Project documentation in `docs/`.
- Fictional support documents in `knowledge-base/`.
- Mock transactional data in `mock-data/`.
- Evaluation cases in `evaluation-data/`.
- Fine-tuning sample formats in `fine-tuning-data/`.
- Python package code under `src/`.
- Tests under `tests/`.
- Environment verification in `scripts/verify_environment.py`.

The implemented code currently focuses on Markdown loading, heading-aware chunking, embedding generation, and early retrieval structure. The README says Qdrant indexing, complete retrieval, grounded generation, FastAPI, LangGraph, structured tools, and UI are still future work.

## Step 1: Confirm The Local Environment

Goal: make sure the project runs from the intended Python 3.11 virtual environment and all required packages are available.

Actions:

1. Open PowerShell in the repository root.
2. Activate the virtual environment:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

3. Run the environment verification script:

   ```powershell
   python .\scripts\verify_environment.py
   ```

How to confirm:

- The command prints `Environment verification passed.`
- Python is reported as version `3.11`.
- The Python executable is inside `.venv`.
- Qdrant local in-memory mode passes.
- CUDA may be available or unavailable; CPU mode is acceptable for current tests.

If it fails:

- Re-run setup:

  ```powershell
  powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
  ```

- Then activate `.venv` again and rerun `python .\scripts\verify_environment.py`.

## Step 2: Run The Existing Test Suite

Goal: establish a clean baseline before adding more features.

Action:

```powershell
python -m pytest -q
```

How to confirm:

- All existing tests pass.
- Pay special attention to:
  - `tests/test_split_documents.py`
  - `tests/test_embed_documents.py`
  - `tests/test_retrieval.py`

Current note:

- `tests/test_retrieval.py` is still a placeholder, so retrieval behavior needs real test coverage in the next implementation phase.

If it fails:

- Fix failing tests before adding new features.
- Avoid changing test expectations until the code behavior and project docs agree.

## Step 3: Check Code Quality

Goal: catch style, import, typing, and simple correctness issues early.

Actions:

```powershell
python -m ruff check .
python -m mypy src tests
```

How to confirm:

- Ruff reports no lint errors.
- Mypy reports no type errors.

If commands are missing:

```powershell
python -m pip install -r requirements-dev.txt
```

Then rerun the checks.

## Step 4: Manually Inspect Core RAG Inputs

Goal: confirm the knowledge base and evaluation files are ready for retrieval work.

Actions:

1. Review the source documents:

   ```powershell
   Get-ChildItem .\knowledge-base
   ```

2. Review retrieval test cases:

   ```powershell
   Get-Content .\evaluation-data\retrieval-test-cases.json
   ```

3. Review answer test cases:

   ```powershell
   Get-Content .\evaluation-data\answer-test-cases.json
   ```

How to confirm:

- Every knowledge-base document has a clear subject.
- Evaluation cases reference documents and sections that actually exist.
- Any mismatch is corrected before writing automated retrieval metrics.

## Step 5: Implement Qdrant Indexing

Goal: store embedded chunks in a vector database so retrieval can query them.

Expected code areas:

- `src/ingestion/index_documents.py`
- `src/embeddings/embed_documents.py`
- `src/ingestion/load_documents.py`
- `src/ingestion/split_documents.py`

Implementation requirements:

- Load Markdown documents from `knowledge-base/`.
- Split documents into chunks with preserved metadata.
- Embed chunks with a deterministic model option for tests and a real model option for local use.
- Create or recreate a Qdrant collection.
- Store each chunk with:
  - `chunk_id`
  - `document_id`
  - `source`
  - `chunk_index`
  - chunk text
  - embedding vector

How to confirm:

- Add or update tests that use Qdrant in-memory mode:

  ```powershell
  python -m pytest tests/test_embed_documents.py tests/test_split_documents.py -q
  ```

- Add indexing tests that confirm:
  - collection is created
  - point count equals embedded chunk count
  - payload metadata is preserved
  - repeated indexing does not silently duplicate records

- Run all tests:

  ```powershell
  python -m pytest -q
  ```

## Step 6: Implement Dense Retrieval

Goal: retrieve relevant policy chunks for a user question.

Expected code areas:

- `src/retrieval/retriever.py`
- `tests/test_retrieval.py`
- `evaluation-data/retrieval-test-cases.json`

Implementation requirements:

- Accept a user question.
- Embed the question with the same embedding model used for document chunks.
- Query Qdrant with `top_k`.
- Return ranked chunks with metadata and scores.
- Keep retrieval independent from answer generation.

How to confirm:

- Replace the placeholder retrieval test with real tests.
- Use a fake or deterministic embedding model for unit tests.
- Use evaluation cases for integration tests.

Suggested command:

```powershell
python -m pytest tests/test_retrieval.py -q
```

Confirmation criteria:

- Retrieval returns the expected document in the top 3 for easy cases.
- Returned chunks include source metadata.
- Empty or unsupported questions are handled without crashing.

Target:

- Reach at least 80% Recall@3 on easy development retrieval cases before moving to generation.

## Step 7: Build Grounded Answer Generation

Goal: generate answers only from retrieved evidence and cite sources.

Expected code areas:

- `src/generation/prompt.py`
- `src/generation/generator.py`
- `src/rag.py`

Implementation requirements:

- Build a prompt that includes:
  - user question
  - retrieved context
  - source identifiers
  - refusal instruction when evidence is insufficient
- Return:
  - answer text
  - citations
  - retrieved source list
  - confidence or evidence status

How to confirm:

- Add tests for prompt formatting.
- Add answer tests based on `evaluation-data/answer-test-cases.json`.
- Confirm forbidden claims are not produced.

Suggested commands:

```powershell
python -m pytest tests -q
python -m ruff check .
python -m mypy src tests
```

Confirmation criteria:

- Policy answers cite knowledge-base sources.
- Unsupported questions are refused or escalated.
- The system does not invent booking, payment, or notification status from policy documents.

## Step 8: Add A Minimal CLI For Local Checks

Goal: make ingestion, indexing, retrieval, and answer checks easy to run manually.

Expected code area:

- `src/cli.py`

Suggested commands to support:

- `index`
- `retrieve`
- `ask`
- `evaluate-retrieval`

Example desired usage:

```powershell
python -m src.cli index
python -m src.cli retrieve "What happens if I cancel 2 hours before my slot?"
python -m src.cli ask "How much advance payment is required?"
python -m src.cli evaluate-retrieval
```

How to confirm:

- Each command exits with code `0` for valid input.
- Invalid input produces a clear error message.
- CLI behavior is covered by tests where practical.

## Step 9: Create Retrieval Evaluation Metrics

Goal: turn retrieval quality into a repeatable measurement.

Expected code areas:

- New evaluation helper under `src/` or `scripts/`.
- `evaluation-data/retrieval-test-cases.json`.

Metrics to calculate:

- Recall@3
- Recall@5
- Mean Reciprocal Rank if expected documents are ranked
- Missing expected source count

How to confirm:

```powershell
python -m src.cli evaluate-retrieval
```

Confirmation criteria:

- Evaluation output includes total cases, passed cases, Recall@3, and failed case details.
- Results are reproducible across runs with the same model and data.
- Failed cases show enough detail to debug chunking or retrieval.

## Step 10: Add Structured Tools After RAG Baseline

Goal: answer current transactional questions from mock data instead of documents.

Expected inputs:

- `mock-data/bookings.json`
- `mock-data/payments.json`
- `mock-data/notifications.json`
- `mock-data/support-tickets.json`

Implementation requirements:

- Add read-only lookup functions for:
  - booking status
  - payment status
  - notification history
  - support ticket history
- Validate IDs such as booking IDs and user IDs.
- Do not embed transactional records into RAG.

How to confirm:

- Add tests for valid lookups, missing records, invalid IDs, and unauthorized access.
- Use the routing cases in `evaluation-data/routing-test-cases.json`.

Confirmation criteria:

- Booking/payment/status questions use tools.
- Policy questions still use RAG.
- Unauthorized or missing records do not produce fabricated answers.

## Step 11: Add LangGraph Routing

Goal: route each user question to the correct path.

Routes to support:

- Policy question -> RAG retrieval and generation.
- Transactional question -> structured tool.
- Unsafe, sensitive, or unclear question -> refusal, clarification, or escalation.

How to confirm:

- Add graph-node tests.
- Add routing tests from `evaluation-data/routing-test-cases.json`.
- Confirm retry limits prevent loops.

Suggested command:

```powershell
python -m pytest tests -q
```

Confirmation criteria:

- Node outputs are testable independently.
- Route decisions include a reason.
- Low-confidence evidence does not produce a confident answer.

## Step 12: Add FastAPI Backend

Goal: expose the support copilot through an API.

Expected endpoints:

- `POST /chat`
- `POST /retrieve`
- `GET /health`

Implementation requirements:

- Validate request and response schemas with Pydantic.
- Return answer, citations, route, and escalation status.
- Keep internal traces out of user-facing responses.

How to confirm:

```powershell
python -m pytest tests -q
uvicorn src.api:app --reload
```

Manual API checks:

```powershell
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:8000/health
```

Confirmation criteria:

- `/health` returns success.
- `/chat` answers policy questions with citations.
- `/chat` routes transactional questions to tools.
- API tests cover schema validation and error paths.

## Step 13: Add Security And Privacy Checks

Goal: prevent the system from leaking prompts, private data, or unrelated user records.

Expected inputs:

- `evaluation-data/adversarial-test-cases.json`
- `docs/14-security-and-privacy.md`

How to confirm:

- Add tests for prompt injection attempts.
- Add tests for attempts to access another user's booking or payment.
- Confirm logs do not store unnecessary sensitive data.

Confirmation criteria:

- The assistant refuses requests to ignore policies or reveal system prompts.
- The assistant does not expose records without valid authorization.
- Sensitive cases escalate when the answer is uncertain.

## Step 14: Add Experiment Logging

Goal: track changes so improvements are explainable.

Expected docs:

- `docs/18-experiment-log-template.md`
- `docs/19-learning-journal-template.md`

How to confirm:

- For each retrieval or prompt experiment, record:
  - date
  - change made
  - metric before
  - metric after
  - failed examples
  - decision

Confirmation criteria:

- Any major retrieval, prompt, or routing change has a written result.
- The chosen implementation is justified by metrics, not only intuition.

## Step 15: Final Confirmation Checklist Before Each Commit

Run this before committing meaningful code changes:

```powershell
python .\scripts\verify_environment.py
python -m pytest -q
python -m ruff check .
python -m mypy src tests
git status --short
```

Confirm:

- Environment verification passes.
- Tests pass.
- Ruff passes.
- Mypy passes.
- `git status --short` only shows files intentionally changed.
- README and relevant docs are updated if behavior or commands changed.

## Suggested Immediate Next Task

The next best implementation task is dense retrieval backed by Qdrant in-memory tests.

Start with:

1. Finish or review `src/ingestion/index_documents.py`.
2. Implement real behavior in `src/retrieval/retriever.py`.
3. Replace the placeholder `tests/test_retrieval.py` with meaningful tests.
4. Run:

   ```powershell
   python -m pytest tests/test_retrieval.py -q
   python -m pytest -q
   ```

Only after dense retrieval is tested should grounded answer generation be expanded.
