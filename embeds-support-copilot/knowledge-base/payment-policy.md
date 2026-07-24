# Payment Policy

- Document ID: `payment-policy-v1`
- Version: `1.0`
- Category: `payments`

> Practice assumptions created for this learning project. These are not final business policies or legal terms.

## Purpose

Explain advance payment, payment deadlines, and payment verification.

## Policy or Procedure

## Advance Payment

Customers must submit a 30% advance payment to continue a booking request. The remaining amount is assumed to be paid at the venue unless the court owner states otherwise.

## Payment Deadline

The payment deadline is 30 minutes from booking creation. If payment is not submitted before the deadline, the booking becomes `expired` and the slot becomes available again.

## Payment Verification

After payment is submitted, the booking changes to `payment_under_review`. Verification may take up to 15 minutes. Support should not confirm a booking until payment is verified.

## Duplicate Payments

Duplicate payments require support review. The chatbot may explain the process but must not promise a refund.

## Examples

- Court price PKR 12,000 means advance payment is PKR 3,600.
- If a customer submits payment at minute 28, support should check payment review status.
- If a payment reference cannot be found, support should request proof and escalate.

## Information Support Should Request

- Booking ID
- Payment reference
- Amount paid
- Payment method
- Screenshot or receipt if available
- Time of payment

## Escalation Conditions

- Duplicate payment
- Missing payment record
- Payment provider outage
- Customer claims amount was deducted but booking expired

## Related Documents

- [Booking Process](booking-process.md)
- [Refund Policy](refund-policy.md)
- [Troubleshooting Guide](troubleshooting-guide.md)

