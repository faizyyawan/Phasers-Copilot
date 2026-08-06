"""Profanity and abuse filtering for customer-visible text."""

from __future__ import annotations

import os
import re

DEFAULT_ABUSE_PATTERNS = (
    r"asshole(?:s)?",
    r"bastard(?:s)?",
    r"bitch(?:es)?",
    r"crap",
    r"damn",
    r"fuck(?:ed|er|ers|ing|s)?",
    r"idiot(?:s)?",
    r"nigg(?:a|as|er|ers)",
    r"shit(?:ty|s)?",
    r"stupid",
)
ABUSE_WARNING_ANSWER = (
    "I'm here to help, but please avoid abusive or offensive language. "
    "Rephrase your question respectfully and I'll do my best to assist."
)


def _configured_patterns() -> tuple[str, ...]:
    extra_patterns = tuple(
        term.strip().lower()
        for term in os.getenv("ABUSE_CENSOR_EXTRA_WORDS", "").split(",")
        if term.strip()
    )
    return DEFAULT_ABUSE_PATTERNS + extra_patterns


def _abuse_pattern() -> re.Pattern[str] | None:
    patterns = _configured_patterns()
    if not patterns:
        return None
    return re.compile(
        r"\b(" + "|".join(patterns) + r")\b",
        flags=re.IGNORECASE,
    )


def _censor_match(match: re.Match[str]) -> str:
    word = match.group(0)
    if len(word) <= 2:
        return "*" * len(word)
    return f"{word[0]}{'*' * (len(word) - 1)}"


def censor_abusive_words(text: str) -> str:
    """Mask configured abusive words without changing unrelated text."""
    pattern = _abuse_pattern()
    if pattern is None:
        return text
    return pattern.sub(_censor_match, text)


def contains_abusive_words(text: str) -> bool:
    """Return true when text contains configured abusive words."""
    pattern = _abuse_pattern()
    if pattern is None:
        return False
    return bool(pattern.search(text))
