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


def test_my_phone_number_is_account_question_not_privacy() -> None:
    decision = route_message("how do i change my phone number")

    assert decision.route == "account_update"


def test_typo_phone_number_question_routes_to_account_update() -> None:
    decision = route_message("how do i cyhange my phone number")

    assert decision.route == "account_update"


def test_typo_account_words_still_route_to_account_update() -> None:
    decision = route_message("how do i update my fone numbr")

    assert decision.route == "account_update"


def test_typo_booking_status_routes_to_booking_tool() -> None:
    decision = route_message("what is bokking BK-1001 sttaus")

    assert decision.route == "get_booking_status"


def test_typo_refund_status_routes_to_payment_tool() -> None:
    decision = route_message("when is my refnd sttaus")

    assert decision.route == "get_payment_status"


def test_typo_notification_history_routes_to_notification_tool() -> None:
    decision = route_message("show whatsap hsitory")

    assert decision.route == "get_notification_history"


def test_irrelevant_question_routes_out_of_scope() -> None:
    decision = route_message("write me a love poem about the moon")

    assert decision.route == "out_of_scope"


def test_identity_questions_route_to_fixed_answers() -> None:
    assert route_message("who are you").route == "bot_identity"
    assert route_message("whoa re u").route == "bot_identity"
    assert route_message("what can u do").route == "bot_identity"
    assert route_message("who am i").route == "user_identity"
