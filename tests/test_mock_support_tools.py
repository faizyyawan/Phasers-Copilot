"""Tests for mock support lookup tools."""

from src.support.responses import payment_status_answer
from src.tools.mock_support_tools import (
    get_booking_status,
    get_notification_history,
    get_payment_status,
    search_previous_tickets,
)


def test_mock_tools_find_records_by_ids() -> None:
    assert get_booking_status("BK-1001")["status"] == "confirmed"  # type: ignore[index]
    assert get_payment_status(payment_id="PAY-2001")[0]["status"] == "verified"
    assert get_notification_history(booking_id="BK-1004")[0]["status"] == (
        "failed_delivery"
    )
    assert search_previous_tickets(ticket_id="TCK-4003")[0]["status"] == "open"


def test_tool_answer_does_not_claim_mutation_for_duplicates() -> None:
    answer = payment_status_answer(
        get_payment_status(booking_id="BK-1008"),
        "BK-1008",
    )

    assert "reviewed by support" in answer
    assert "issued refund" not in answer.lower()
    assert "cancelled" not in answer.lower()
    assert "changed availability" not in answer.lower()
