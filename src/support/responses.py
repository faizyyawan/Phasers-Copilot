"""Deterministic customer-facing support responses."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

GREETING_ANSWER = (
    "Hi! I can help with bookings, payments, refunds, cancellations, account "
    "questions, and troubleshooting. What would you like to know?"
)
SMALLTALK_CLOSE_ANSWER = (
    "You're welcome. Send me any booking, payment, refund, or account question "
    "whenever you need help."
)


def handoff_answer(reason: str | None = None) -> str:
    """Return safe handoff/refusal text."""
    if reason == "privacy":
        return (
            "I can't share another customer's private booking details. A support "
            "agent can help after authorization is verified."
        )
    if reason == "refund_guarantee":
        return (
            "I can't guarantee a refund. Refund eligibility depends on the booking, "
            "payment record, cancellation timing, and support review."
        )
    if reason == "unsupported_action":
        return (
            "I can't make changes like cancelling bookings, issuing refunds, or "
            "changing availability. I can explain the next support step or help you "
            "check the current status."
        )
    if reason == "legal":
        return (
            "I can't advise on legal compensation. I can explain the support policy "
            "and help route the case to a human review."
        )
    if reason == "fraud":
        return (
            "This should be reviewed by support. Please share the booking or payment "
            "reference and any receipt or evidence so the team can investigate."
        )
    return (
        "This looks like a case for human support review. Please share the relevant "
        "booking or payment reference and a short description of what happened."
    )


def missing_identifier_answer(route: str) -> str:
    """Ask for the identifier required by a tool route."""
    if route == "get_booking_status":
        return "Please send the booking ID, such as BK-1001, so I can check it."
    if route == "get_payment_status":
        return (
            "Please send the payment ID, such as PAY-2001, or the booking ID linked "
            "to the payment."
        )
    if route == "get_notification_history":
        return (
            "Please send the notification ID or booking ID so I can check the "
            "message history."
        )
    if route == "search_previous_tickets":
        return (
            "Please send the ticket ID, booking ID, or topic you want me to search."
        )
    if route == "get_court_availability":
        return (
            "Live court availability needs the court, date, and availability system. "
            "I can explain booking policy, but I can't confirm live slots from the "
            "knowledge base alone."
        )
    return "Please share the reference ID so I can check the right record."


def no_evidence_answer() -> str:
    """Return fallback when retrieval does not provide usable evidence."""
    return (
        "I don't have enough policy information to answer that confidently. Please "
        "share a booking or payment reference if this is about a specific case, or "
        "contact support for review."
    )


def out_of_scope_answer() -> str:
    """Return fallback for questions outside the support copilot domain."""
    return (
        "I'm sorry, but I can't help with that kind of request. I can help with "
        "bookings, payments, refunds, cancellations, account questions, and "
        "troubleshooting."
    )


def account_update_answer() -> str:
    """Return safe guidance for account detail updates."""
    return (
        "I can't update account details directly in this chat. To change your phone "
        "number or email, use the account settings workflow or contact support. "
        "Support should verify your identity before changing account information."
    )


def bot_identity_answer() -> str:
    """Explain what the assistant is and what it can help with."""
    return (
        "I'm Embeds Support Copilot, a support assistant for bookings, payments, "
        "refunds, cancellations, account questions, and troubleshooting."
    )


def user_identity_answer() -> str:
    """Explain user identity limits without pretending to know the user."""
    return (
        "I can't identify who you are from this chat alone. If your question is "
        "about a booking, payment, notification, or ticket, share the relevant "
        "reference ID and I can help with that record."
    )


def _money(amount: Any, currency: Any = "PKR") -> str:
    if isinstance(amount, int | float):
        return f"{currency} {amount:,.0f}"
    return f"{currency} {amount}"


def booking_status_answer(booking: dict[str, Any] | None, booking_id: str) -> str:
    """Format booking lookup result."""
    if not booking:
        return (
            f"I couldn't find booking {booking_id}. Please recheck the booking ID. "
            "If you have a receipt or screenshot, support can review it."
        )
    status = str(booking.get("status", "unknown")).replace("_", " ")
    slot = booking.get("slot_start", "the booked slot")
    court = booking.get("court_id", "the court")
    advance = _money(booking.get("advance_required"), "PKR")
    return (
        f"Booking {booking['booking_id']} is currently {status}. It is for {court} "
        f"at {slot}. The advance amount for this booking is {advance}."
    )


def payment_status_answer(payments: Sequence[dict[str, Any]], reference: str) -> str:
    """Format payment lookup result."""
    if not payments:
        return (
            f"I couldn't find a payment record for {reference}. Please check the "
            "reference, or share a receipt screenshot for support review."
        )
    if len(payments) > 1:
        refs = ", ".join(str(payment.get("reference")) for payment in payments)
        return (
            "I found multiple payment records for this booking, so this should be "
            f"reviewed by support. The listed references are {refs}."
        )
    payment = payments[0]
    status = str(payment.get("status", "unknown")).replace("_", " ")
    amount = _money(payment.get("amount"), payment.get("currency", "PKR"))
    verified_at = payment.get("verified_at")
    suffix = f" It was verified at {verified_at}." if verified_at else ""
    return (
        f"Payment {payment['payment_id']} for booking {payment['booking_id']} is "
        f"currently {status}. Amount: {amount}.{suffix}"
    )


def notification_history_answer(
    notifications: Sequence[dict[str, Any]],
    reference: str,
) -> str:
    """Format notification lookup result."""
    if not notifications:
        return (
            f"I couldn't find notification history for {reference}. Please recheck "
            "the reference or ask support to review delivery logs."
        )
    lines = []
    for notification in notifications:
        kind = str(notification.get("type", "notification")).replace("_", " ")
        status = str(notification.get("status", "unknown")).replace("_", " ")
        sent_at = notification.get("sent_at", "unknown time")
        lines.append(f"{kind} was {status} at {sent_at}")
    return "I found this notification history: " + "; ".join(lines) + "."


def tickets_answer(tickets: Sequence[dict[str, Any]], reference: str) -> str:
    """Format support ticket search result."""
    if not tickets:
        return (
            f"I couldn't find a support ticket for {reference}. If the issue is "
            "still active, support can create a new review case."
        )
    summaries = [
        (
            f"{ticket['ticket_id']} is {ticket.get('status', 'unknown')} "
            f"({ticket.get('priority', 'normal')} priority): "
            f"{ticket.get('summary', 'No summary')}"
        )
        for ticket in tickets
    ]
    return "I found these support tickets: " + "; ".join(summaries) + "."
