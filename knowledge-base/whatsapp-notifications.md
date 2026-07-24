# WhatsApp Notifications

- Document ID: `whatsapp-notifications-v1`
- Version: `1.0`
- Category: `notifications`

> Practice assumptions created for this learning project. These are not final business policies or legal terms.

## Purpose

Explain notification types, delivery failures, invalid phone numbers, opt-out behavior, and provider issues.

## Policy or Procedure

Notification events may include booking request received, payment received, booking confirmed, booking reminder, booking cancelled, and refund initiated.

Failed delivery can happen because of invalid phone number, WhatsApp opt-out, provider failure, blocked recipient, network delay, or template issue.

If a user opted out, support should explain that WhatsApp messages may not be delivered until opt-in is restored. The chatbot should not claim a message was sent unless notification history confirms it.

## Examples

- A confirmed booking should usually trigger a booking confirmed message.
- A reminder may be sent before the slot.
- Provider failure should be escalated if many users are affected.

## Information Support Should Request

- Booking ID
- Phone number confirmation
- Expected message type
- Approximate time
- Screenshot of any error if available

## Escalation Conditions

- Repeated failed delivery
- Invalid number cannot be corrected by user
- Provider outage suspected
- User did not receive cancellation or refund notification

## Related Documents

- [Booking Process](booking-process.md)
- [Customer Account Guide](customer-account-guide.md)
- [Troubleshooting Guide](troubleshooting-guide.md)

