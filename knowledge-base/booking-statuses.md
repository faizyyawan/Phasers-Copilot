# Booking Statuses

- Document ID: `booking-statuses-v1`
- Version: `1.0`
- Category: `booking`

> Practice assumptions created for this learning project. These are not final business policies or legal terms.

## Purpose

Define booking statuses used by Embeds Support Copilot.

## Policy or Procedure

- `pending_payment`: Booking was created and is waiting for 30% advance payment.
- `payment_under_review`: Customer submitted payment and verification is pending.
- `confirmed`: Payment was verified and the court slot is reserved.
- `cancelled`: Booking was cancelled by the customer, court owner, support, or system rule.
- `expired`: Payment was not submitted before the 30-minute deadline.
- `completed`: The booked slot time has passed and the booking was fulfilled.
- `refund_pending`: A refund case is approved or being reviewed for processing.
- `refunded`: Refund has been marked completed in the payment system.

## Examples

- A booking can move from `pending_payment` to `expired`.
- A booking can move from `payment_under_review` to `confirmed`.
- A cancelled booking may move to `refund_pending` only if support review indicates eligibility.

## Information Support Should Request

- Booking ID
- User identity confirmation
- Current status from structured tool
- Payment reference if relevant

## Escalation Conditions

- Status is inconsistent with payment records.
- Status changed unexpectedly.
- User disputes `expired` or `cancelled` status.

## Related Documents

- [Booking Process](booking-process.md)
- [Cancellation Policy](cancellation-policy.md)
- [Refund Policy](refund-policy.md)

