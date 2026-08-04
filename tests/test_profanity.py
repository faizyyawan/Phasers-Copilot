"""Tests for customer-visible profanity filtering."""

from src.safety.profanity import censor_abusive_words, contains_abusive_words


def test_censor_abusive_words_masks_terms_case_insensitively() -> None:
    assert censor_abusive_words("This is Damn bad.") == "This is D*** bad."


def test_censor_abusive_words_does_not_change_substrings() -> None:
    assert censor_abusive_words("classic assumption") == "classic assumption"


def test_contains_abusive_words_detects_terms() -> None:
    assert contains_abusive_words("fuck") is True
    assert contains_abusive_words("refund status please") is False
