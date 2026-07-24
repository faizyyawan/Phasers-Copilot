# Testing Strategy

## Test Types

- Unit tests: Validate pure functions such as metadata parsing, ID validation, and prompt formatting.
- Integration tests: Validate retriever, vector store, database, and API boundaries together.
- Retrieval tests: Measure expected documents and sections for questions.
- Prompt regression tests: Detect answer drift after prompt changes.
- Graph-node tests: Test LangGraph nodes independently.
- Tool tests: Verify read-only tool validation, authorization, and error handling.
- API tests: Validate request/response schemas and auth behavior.
- Fine-tuning evaluation: Compare base model and adapter on held-out behavior tasks.
- Security tests: Test prompt injection, authorization, and data redaction.
- Adversarial tests: Test requests to ignore policies, reveal prompts, or access other users' data.
- End-to-end tests: Simulate complete user conversations.

## Retrieval Test Template

```json
{
  "question": "How much advance must I pay?",
  "expected_documents": ["payment-policy.md"],
  "expected_sections": ["Advance payment"],
  "top_k": 3
}
```

## Answer Test Template

```json
{
  "question": "Can I get a refund if I cancel 2 hours before the slot?",
  "expected_answer_points": ["Less than 6 hours is generally non-refundable", "Do not guarantee outcome"],
  "forbidden_claims": ["You will definitely get a refund"]
}
```

## Tool Test Template

```json
{
  "tool": "get_booking_status",
  "input": {"booking_id": "BK-1001", "user_id": "USR-001"},
  "expected_status": "success",
  "expected_fields": ["booking_id", "status"]
}
```

## Graph Test Template

```json
{
  "question": "Where is my payment for BK-1001?",
  "expected_route": "get_payment_status",
  "expected_entities": {"booking_id": "BK-1001"}
}
```

