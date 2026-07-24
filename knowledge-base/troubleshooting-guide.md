# Troubleshooting Guide

- Document ID: `troubleshooting-guide-v1`
- Version: `1.0`
- Category: `troubleshooting`

> Practice assumptions created for this learning project. These are not final business policies or legal terms.

## Purpose

Provide support procedures for common issues.

## Payment Submitted but Booking Still Pending

- Symptoms: User paid but sees `pending_payment`.
- Possible causes: Payment not submitted, delayed provider callback, wrong reference.
- Procedure: Request booking ID and payment reference; check payment tool.
- Information to request: Booking ID, amount, time, receipt.
- Escalation: Payment deducted but no record exists.

## Confirmation Message Not Received

- Symptoms: Booking confirmed but no WhatsApp message.
- Possible causes: Invalid number, opt-out, provider delay.
- Procedure: Check notification history tool.
- Information to request: Booking ID and phone confirmation.
- Escalation: Repeated failed delivery or provider outage.

## Slot Unavailable

- Symptoms: User cannot select desired time.
- Possible causes: Slot booked, expired slot not released yet, owner blocked availability.
- Procedure: Check current availability tool in future implementation.
- Information to request: Court, date, time.
- Escalation: Slot appears unavailable due to system error.

## Duplicate Payment

- Symptoms: User paid twice.
- Possible causes: Retried payment, provider delay, wrong reference.
- Procedure: Request both references; check payment tool.
- Information to request: Booking ID, both payment references, amounts.
- Escalation: Always escalate for review.

## Incorrect Booking Date

- Symptoms: User booked wrong date.
- Possible causes: User selection error or UI misunderstanding.
- Procedure: Explain cancellation policy and check if rescheduling support is available.
- Information to request: Booking ID and desired date.
- Escalation: Confirmed booking needs exception handling.

## Wrong Phone Number

- Symptoms: Messages go to wrong number or fail.
- Possible causes: Account data error.
- Procedure: Verify identity and ask user to update account details.
- Information to request: Account identity and correct number.
- Escalation: Active booking notifications affected.

## Court Owner Cannot Change Availability

- Symptoms: Owner cannot block/open slots.
- Possible causes: Permission issue, locked confirmed slot, system error.
- Procedure: Verify owner role and affected slots.
- Information to request: Court ID, owner account, slot details.
- Escalation: Confirmed bookings affected.

## Booking Expired

- Symptoms: Booking status is `expired`.
- Possible causes: Payment missed 30-minute deadline.
- Procedure: Explain expired slots become available again; check payment if user claims payment submitted.
- Information to request: Booking ID and payment evidence.
- Escalation: Payment deducted before deadline but booking expired.

## Refund Delayed

- Symptoms: User expected refund but has not received it.
- Possible causes: Review pending, payment provider delay, failed refund.
- Procedure: Check payment/refund status tool.
- Information to request: Booking ID, refund request date.
- Escalation: Failed or long-pending refund.

## Booking ID Not Found

- Symptoms: Tool cannot find booking ID.
- Possible causes: Typo, wrong account, old deleted test data.
- Procedure: Ask user to recheck ID and account.
- Information to request: Screenshot, date, court, phone/email.
- Escalation: User shows valid receipt but booking missing.

## Related Documents

- [Payment Policy](payment-policy.md)
- [Refund Policy](refund-policy.md)
- [WhatsApp Notifications](whatsapp-notifications.md)

