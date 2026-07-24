# Data Model

This is a conceptual model only. Do not generate migrations or ORM models from this file without designing them yourself.

## Entities

| Entity | Purpose | Proposed fields | Relationships | Transactional fields | RAG-indexed fields | Sensitive-data notes |
|---|---|---|---|---|---|---|
| User | Customer or staff identity. | user_id, name, phone, role, created_at | Has bookings, tickets, conversations | phone, role | None | Phone and identity are sensitive. |
| Court | Bookable venue/court. | court_id, owner_id, name, sport, location, status | Has bookings and availability | availability status | Public descriptions only | Owner data may be private. |
| Booking | Reserved or attempted slot. | booking_id, user_id, court_id, slot_start, status, deadline | Has payment, notifications, tickets | status, slot, deadline | None | User-specific. |
| Payment | Advance or refund payment record. | payment_id, booking_id, amount, status, reference, verified_at | Belongs to booking | status, reference, amount | None | Payment references are sensitive. |
| Notification | WhatsApp/SMS/email event. | notification_id, booking_id, type, status, provider_message_id | Belongs to booking | delivery status | None | Provider IDs and phone hints are sensitive. |
| SupportConversation | Chat session. | conversation_id, user_id, status, created_at | Has messages and traces | status | None | Contains user text. |
| SupportMessage | User or assistant message. | message_id, conversation_id, role, content, created_at | Belongs to conversation | content | Only sanitized examples | May contain personal data. |
| SupportTicket | Human support case. | ticket_id, user_id, booking_id, category, status, summary | Related to booking and conversation | status, assignment | Sanitized summaries only | Do not expose across users. |
| KnowledgeDocument | Source document. | document_id, title, category, version, status, source_path | Has chunks | status, version | Yes | Avoid private data. |
| KnowledgeChunk | Searchable evidence unit. | chunk_id, document_id, text, section, metadata | Belongs to document | active status | Yes | Must not contain secrets. |
| RetrievalTrace | Retrieval debug record. | trace_id, query, chunks, scores, prompt_version | Belongs to conversation | scores | No | Redact user data. |
| Escalation | Human review item. | escalation_id, conversation_id, reason, status, assigned_to | Related to ticket | status, reason | No | Contains sensitive context. |
| EvaluationCase | Test example. | case_id, question, expected_sources, labels | In evaluation runs | labels | No | Use fake data only. |
| PromptVersion | Versioned prompt. | prompt_id, name, version, content_hash | Used by runs | active version | No | May include internal instructions. |
| ModelVersion | Model configuration. | model_id, provider, base_model, adapter, settings | Used by runs | active version | No | Track license and source. |

