# Booking Process

- Document ID: `booking-process-v1`
- Version: `1.0`
- Category: `booking`

> Practice assumptions created for this learning project. These are not final business policies or legal terms.

## Purpose

Explain how a customer books a court and how booking status changes during payment verification.

## Policy or Procedure

1. The user selects a court, date, and time slot.
2. The system creates a booking with status `pending_payment`.
3. The customer must submit a 30% advance payment within 30 minutes.
4. Submitted payment changes the booking to `payment_under_review`.
5. Payment verification may take up to 15 minutes.
6. Verified payment changes the booking to `confirmed`.
7. If payment is not submitted before the deadline, the booking becomes `expired`.
8. An expired slot becomes available again.

## Examples

- If a slot costs PKR 10,000, the advance is PKR 3,000.
- If booking `BK-1001` is still `pending_payment`, support should check whether the payment deadline has passed.
- If payment was submitted, support should check payment review status before telling the customer to book again.

## Information Support Should Request

- Booking ID
- Customer account phone or email
- Court name
- Date and time slot
- Payment reference if payment was submitted

## Escalation Conditions

- Customer claims payment was submitted but no payment record exists.
- Two users claim the same slot.
- Booking expired after a reported provider outage.
- Customer asks for an exception to normal booking flow.

## Related Documents

- [Booking Statuses](booking-statuses.md)
- [Payment Policy](payment-policy.md)
- [Troubleshooting Guide](troubleshooting-guide.md)

