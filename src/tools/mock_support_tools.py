"""Read-only support lookups backed by local mock JSON data."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[2] / "mock-data"


def _load_json(name: str) -> list[dict[str, Any]]:
    path = DATA_DIR / name
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise TypeError(f"{name} must contain a JSON list.")
    return [item for item in payload if isinstance(item, dict)]


@lru_cache(maxsize=1)
def bookings() -> list[dict[str, Any]]:
    """Return mock bookings."""
    return _load_json("bookings.json")


@lru_cache(maxsize=1)
def payments() -> list[dict[str, Any]]:
    """Return mock payments."""
    return _load_json("payments.json")


@lru_cache(maxsize=1)
def notifications() -> list[dict[str, Any]]:
    """Return mock notifications."""
    return _load_json("notifications.json")


@lru_cache(maxsize=1)
def support_tickets() -> list[dict[str, Any]]:
    """Return mock support tickets."""
    return _load_json("support-tickets.json")


def get_booking_status(booking_id: str) -> dict[str, Any] | None:
    """Find one booking by ID."""
    booking_id = booking_id.upper()
    return next(
        (booking for booking in bookings() if booking.get("booking_id") == booking_id),
        None,
    )


def get_payment_status(
    payment_id: str | None = None,
    booking_id: str | None = None,
) -> list[dict[str, Any]]:
    """Find payments by payment ID or booking ID."""
    payment_id = payment_id.upper() if payment_id else None
    booking_id = booking_id.upper() if booking_id else None
    return [
        payment
        for payment in payments()
        if (payment_id and payment.get("payment_id") == payment_id)
        or (booking_id and payment.get("booking_id") == booking_id)
    ]


def get_notification_history(
    notification_id: str | None = None,
    booking_id: str | None = None,
) -> list[dict[str, Any]]:
    """Find notifications by notification ID or booking ID."""
    notification_id = notification_id.upper() if notification_id else None
    booking_id = booking_id.upper() if booking_id else None
    return [
        notification
        for notification in notifications()
        if (
            notification_id
            and notification.get("notification_id") == notification_id
        )
        or (booking_id and notification.get("booking_id") == booking_id)
    ]


def search_previous_tickets(
    ticket_id: str | None = None,
    booking_id: str | None = None,
    topic: str | None = None,
) -> list[dict[str, Any]]:
    """Find support tickets by ID, booking ID, or topic/category text."""
    ticket_id = ticket_id.upper() if ticket_id else None
    booking_id = booking_id.upper() if booking_id else None
    topic = topic.lower() if topic else None
    return [
        ticket
        for ticket in support_tickets()
        if (ticket_id and ticket.get("ticket_id") == ticket_id)
        or (booking_id and ticket.get("booking_id") == booking_id)
        or (
            topic
            and (
                topic in str(ticket.get("category", "")).lower()
                or topic in str(ticket.get("summary", "")).lower()
            )
        )
    ]
