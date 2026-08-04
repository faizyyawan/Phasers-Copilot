"""Profanity and abuse filtering for customer-visible text."""

from __future__ import annotations

import os
import re

DEFAULT_CENSORED_TERMS = (
    "asshole",
    "bastard",
    "bitch",
    "crap",
    "damn",
    "fuck",
    "fucking",
    "idiot",
    "shit",
    "stupid",
)
ABUSE_WARNING_ANSWER = (
    "I'm here to help, but please avoid abusive or offensive language. "
    "Rephrase your question respectfully and I'll do my best to assist."
)


def _configured_terms() -> tuple[str, ...]:
    extra_terms = tuple(
        term.strip().lower()
        for term in os.getenv("ABUSE_CENSOR_EXTRA_WORDS", "").split(",")
        if term.strip()
    )
    return DEFAULT_CENSORED_TERMS + extra_terms


def _censor_match(match: re.Match[str]) -> str:
    word = match.group(0)
    if len(word) <= 2:
        return "*" * len(word)
    return f"{word[0]}{'*' * (len(word) - 1)}"


def censor_abusive_words(text: str) -> str:
    """Mask configured abusive words without changing unrelated text."""
    terms = _configured_terms()
    if not terms:
        return text

    pattern = re.compile(
        r"\b(" + "|".join(re.escape(term) for term in terms) + r")\b",
        flags=re.IGNORECASE,
    )
    return pattern.sub(_censor_match, text)


def contains_abusive_words(text: str) -> bool:
    """Return true when text contains configured abusive words."""
    terms = _configured_terms()
    if not terms:
        return False

    pattern = re.compile(
        r"\b(" + "|".join(re.escape(term) for term in terms) + r")\b",
        flags=re.IGNORECASE,
    )
    return bool(pattern.search(text))
