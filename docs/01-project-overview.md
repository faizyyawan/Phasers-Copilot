# Project Overview

> Practice assumptions created for this learning project. These are not final business policies or legal terms.

## Business Scenario

Embeds is a fictional sports-court booking platform where customers reserve football, tennis, badminton, basketball, and cricket facilities. Court owners publish available time slots, receive booking requests, and confirm slots after advance payment verification.

## Problem Being Solved

Support teams answer repetitive questions about booking, payment, cancellation, refund, and notification issues. The final copilot should reduce repetitive support work while escalating cases that require judgment or private transactional data.

## Customer-Support Use Cases

- Explain how to book a court.
- Explain the 30% advance requirement.
- Explain why a booking is pending.
- Explain cancellation and refund assumptions.
- Troubleshoot missing WhatsApp messages.
- Look up the current status of a specific booking by tool.

## Court-Owner Support Use Cases

- Explain how availability should be updated.
- Explain why a slot may appear unavailable.
- Troubleshoot availability changes.
- Explain notification behavior after confirmations or cancellations.

## Administrative Support Use Cases

- Review escalated disputes.
- Monitor refund delays.
- Audit tool traces and source citations.
- Evaluate routing quality and refusal behavior.

## Stakeholders

- Customers
- Court owners
- Support agents
- Administrators
- Engineering learner building the system

## Project Scope

The learning project includes documentation, RAG, retrieval evaluation, structured read-only tools, LangGraph orchestration, mock transactional data, and small QLoRA behavior experiments.

## Out of Scope

- Real payment processing
- Real WhatsApp integration
- Automatic refunds
- Automatic cancellations
- Legal advice
- Production policy guarantees
- Real customer data

## Assumptions

- Booking starts as `pending_payment`.
- A 30% advance payment is required.
- Payment must be submitted within 30 minutes.
- Payment review may take up to 15 minutes.
- Cancellation eligibility depends on time before slot and support review.
- The chatbot must not guarantee refunds or cancellations.

## Constraints

- RAG documents may be stale unless versioned and reindexed.
- Semantic retrieval is not reliable for exact booking IDs.
- Current booking/payment/notification state must come from tools.
- Fine-tuning data must avoid embedding changing policy facts.

## Expected Final Capabilities

The final chatbot should answer questions such as:

- How do I book a court?
- How much advance payment is required?
- Why is my booking still pending?
- Can I cancel my booking?
- When will my refund arrive?
- Why did I not receive a WhatsApp message?
- How can a court owner update availability?
- What is the current status of booking BK-1001?

The question "What is the current status of booking BK-1001?" requires a structured tool because the answer depends on current transactional data, not document retrieval alone.

