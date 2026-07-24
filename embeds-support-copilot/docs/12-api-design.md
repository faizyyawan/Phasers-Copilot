# API Design

This file documents future endpoints only. It does not implement them.

## Authentication

All user-specific endpoints should require authentication. Support and admin endpoints should require role-based authorization.

## Endpoints

### POST /api/v1/support/chat

Request:

```json
{
  "conversation_id": "CONV-001",
  "message": "What is the status of booking BK-1001?",
  "stream": false
}
```

Response:

```json
{
  "conversation_id": "CONV-001",
  "answer": "Booking BK-1001 is confirmed.",
  "sources": [],
  "tool_calls": [{"tool": "get_booking_status", "status": "success"}],
  "needs_human": false
}
```

Validation errors: missing message, invalid conversation ID, unauthorized booking reference.

Streaming: Use server-sent events or WebSocket later. Stream final answer text, not raw private tool traces.

Idempotency: Include an idempotency key for retrying user turns safely.

### GET /api/v1/conversations/{conversation_id}

Returns authorized conversation history and public-safe trace summaries.

### POST /api/v1/documents

Future endpoint for adding knowledge documents. Requires admin role. Request includes title, category, version, and content.

### POST /api/v1/documents/reindex

Future endpoint for starting reindexing. Requires admin role and idempotency key.

### GET /api/v1/escalations

Returns support escalations for authorized support users.

### POST /api/v1/escalations/{id}/approve

Approves a proposed response or action after human review. Requires support/admin authorization.

### POST /api/v1/escalations/{id}/reject

Rejects an escalation proposal and records reason.

### GET /api/v1/evaluations

Returns evaluation run summaries, dataset versions, metrics, and regressions.

### GET /health

Returns service health without exposing secrets.

## Common Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "booking_id is required",
    "request_id": "REQ-001"
  }
}
```

