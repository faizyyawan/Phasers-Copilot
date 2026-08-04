"""Tests for support route and entity detection."""

from src.routing.router import route_message


def test_greeting_routes_without_tool() -> None:
    decision = route_message("hello")

    assert decision.route == "greeting"
    assert decision.entities == {}


def test_thanks_routes_without_tool() -> None:
    decision = route_message("thanks")

    assert decision.route == "smalltalk_close"


def test_policy_question_routes_to_rag() -> None:
    decision = route_message("What is the refund policy?")

    assert decision.route == "rag_policy"


def test_booking_payment_notification_and_ticket_routes() -> None:
    assert route_message("What is booking BK-1001 status?").route == (
        "get_booking_status"
    )
    assert route_message("Did payment PAY-2001 verify?").route == (
        "get_payment_status"
    )
    assert route_message("Did WhatsApp deliver for BK-1004?").route == (
        "get_notification_history"
    )
    assert route_message("Show ticket TCK-4003").route == (
        "search_previous_tickets"
    )


def test_handoff_routes_for_privacy_and_refund_guarantee() -> None:
    privacy = route_message("Can I get another customer's phone number?")
    refund = route_message("Guarantee my refund now")

    assert privacy.route == "human_escalation"
    assert privacy.handoff_reason == "privacy"
    assert refund.route == "human_escalation"
    assert refund.handoff_reason == "refund_guarantee"
