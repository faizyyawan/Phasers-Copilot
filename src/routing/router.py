"""Route support chat turns before retrieval or mock tool lookup."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

BOOKING_ID_RE = re.compile(r"\bBK-\d+\b", re.IGNORECASE)
PAYMENT_ID_RE = re.compile(r"\bPAY-\d+\b", re.IGNORECASE)
NOTIFICATION_ID_RE = re.compile(r"\bNTF-\d+\b", re.IGNORECASE)
TICKET_ID_RE = re.compile(r"\bTCK-\d+\b", re.IGNORECASE)
COURT_ID_RE = re.compile(r"\bCRT-\d+\b", re.IGNORECASE)
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
HOURS_BEFORE_RE = re.compile(
    r"\b(\d+)\s*(?:hours?|hrs?)\s+before\b",
    re.IGNORECASE,
)

GREETING_RE = re.compile(
    r"^\s*(hi|hello|hey|yo|salam|assalam(?:\s+o\s+alaikum)?|good\s+"
    r"(morning|afternoon|evening))[\s!.?,]*$",
    re.IGNORECASE,
)
SMALLTALK_CLOSE_RE = re.compile(
    r"^\s*(thanks?|thank\s+you|ok(?:ay)?|bye|goodbye|cool|great)[\s!.?,]*$",
    re.IGNORECASE,
)

HANDOFF_PATTERNS = (
    r"\bguarantee\b.*\brefund\b",
    r"\bpromise\b.*\brefund\b",
    r"\bfraud\b",
    r"\blegal\b|\bcompensation\b",
    r"\bdispute|disputed\b",
    r"\banother customer\b|\bsomeone else\b|\bother user's\b",
    r"\bignore\b.*\b(policy|rules?)\b",
    r"\b(cancel|issue|approve|change)\b.*\b(now|automatically|for me)\b",
)
AVAILABILITY_WORDS = ("available", "availability", "free slot", "slot free")
NOTIFICATION_WORDS = ("notification", "whatsapp", "message", "deliver")
TICKET_WORDS = ("ticket", "previous", "case")
PAYMENT_WORDS = ("payment", "paid", "pay", "refund", "duplicate", "verify")
BOOKING_WORDS = ("booking", "status", "expire", "expired", "confirmed")
ACCOUNT_WORDS = (
    "account",
    "email",
    "login",
    "password",
    "phone",
    "profile",
    "number",
)
SUPPORT_SCOPE_WORDS = (
    AVAILABILITY_WORDS
    + NOTIFICATION_WORDS
    + TICKET_WORDS
    + PAYMENT_WORDS
    + BOOKING_WORDS
    + ACCOUNT_WORDS
    + (
        "advance",
        "app",
        "cancel",
        "cancellation",
        "court",
        "error",
        "owner",
        "policy",
        "support",
        "troubleshoot",
    )
)
TYPO_MATCH_THRESHOLD = 0.78
TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class RouteDecision:
    """Routing result for one chat message."""

    route: str
    entities: dict[str, str] = field(default_factory=dict)
    handoff_reason: str | None = None


def _first(regex: re.Pattern[str], message: str) -> str | None:
    match = regex.search(message)
    return match.group(0).upper() if match else None


def extract_entities(message: str) -> dict[str, str]:
    """Extract support identifiers from the message."""
    entities: dict[str, str] = {}
    for key, regex in (
        ("booking_id", BOOKING_ID_RE),
        ("payment_id", PAYMENT_ID_RE),
        ("notification_id", NOTIFICATION_ID_RE),
        ("ticket_id", TICKET_ID_RE),
        ("court_id", COURT_ID_RE),
        ("date", DATE_RE),
    ):
        value = _first(regex, message)
        if value:
            entities[key] = value
    hours_match = HOURS_BEFORE_RE.search(message)
    if hours_match:
        entities["hours_before_slot"] = hours_match.group(1)
    return entities


def _tokens(message: str) -> list[str]:
    return TOKEN_RE.findall(message.lower())


def _similar_enough(left: str, right: str) -> bool:
    if min(len(left), len(right)) < 4:
        return left == right
    return SequenceMatcher(None, left, right).ratio() >= TYPO_MATCH_THRESHOLD


def _has_word(message_tokens: list[str], word: str) -> bool:
    word_tokens = TOKEN_RE.findall(word.lower())
    if not word_tokens:
        return False
    if len(word_tokens) > 1:
        return " ".join(word_tokens) in " ".join(message_tokens)
    target = word_tokens[0]
    return any(_similar_enough(token, target) for token in message_tokens)


def _has_any(message: str, words: tuple[str, ...]) -> bool:
    message_tokens = _tokens(message)
    return any(_has_word(message_tokens, word) for word in words)


def _handoff_reason(message: str) -> str | None:
    lowered = message.lower()
    if re.search(
        r"\banother customer\b|\bsomeone else\b|\bother user's\b",
        lowered,
    ):
        return "privacy"
    if re.search(r"\bfraud\b", lowered):
        return "fraud"
    if re.search(r"\blegal\b|\bcompensation\b", lowered):
        return "legal"
    if re.search(r"\bguarantee\b.*\brefund\b|\bpromise\b.*\brefund\b", lowered):
        return "refund_guarantee"
    if re.search(r"\bdispute|disputed\b", lowered):
        return "dispute"
    if re.search(r"\bignore\b.*\b(policy|rules?)\b", lowered):
        return "policy_override"
    if re.search(r"\b(cancel|issue|approve|change)\b.*\b(now|automatically|for me)\b", lowered):
        return "unsupported_action"
    return None


def route_message(message: str) -> RouteDecision:
    """Choose the safest route for one customer message."""
    stripped = message.strip()
    entities = extract_entities(stripped)
    reason = _handoff_reason(stripped)
    if reason:
        return RouteDecision(
            route="human_escalation",
            entities=entities,
            handoff_reason=reason,
        )
    if GREETING_RE.fullmatch(stripped):
        return RouteDecision(route="greeting", entities=entities)
    if SMALLTALK_CLOSE_RE.fullmatch(stripped):
        return RouteDecision(route="smalltalk_close", entities=entities)
    lowered = stripped.lower()
    if re.search(r"\b(who|whoa|what)\s+(are|r|re)\s+(you|u)\b", lowered):
        return RouteDecision(route="bot_identity", entities=entities)
    if re.search(r"\bwhat\s+can\s+(you|u)\s+do\b", lowered):
        return RouteDecision(route="bot_identity", entities=entities)
    if re.search(r"\b(who|what)\s+(am|m)\s+(i|me)\b", lowered):
        return RouteDecision(route="user_identity", entities=entities)
    if not entities and not _has_any(stripped, SUPPORT_SCOPE_WORDS):
        return RouteDecision(route="out_of_scope", entities=entities)
    if (
        re.search(r"\bhow\s+do\s+i\b", stripped.lower())
        or _has_any(stripped, ("change", "update", "edit", "replace", "modify"))
    ) and _has_any(
        stripped,
        ("phone", "number", "email", "password", "account"),
    ):
        return RouteDecision(route="account_update", entities=entities)

    if entities.get("notification_id") or (
        entities.get("booking_id") and _has_any(stripped, NOTIFICATION_WORDS)
    ):
        return RouteDecision(route="get_notification_history", entities=entities)
    if entities.get("ticket_id") or (
        entities.get("booking_id") and _has_any(stripped, TICKET_WORDS)
    ):
        return RouteDecision(route="search_previous_tickets", entities=entities)
    if entities.get("payment_id") or (
        entities.get("booking_id") and _has_any(stripped, PAYMENT_WORDS)
    ):
        return RouteDecision(route="get_payment_status", entities=entities)
    if entities.get("booking_id") and _has_any(stripped, BOOKING_WORDS):
        return RouteDecision(route="get_booking_status", entities=entities)
    if (
        "owner" in stripped.lower()
        and _has_any(stripped, ("availability", "available"))
        and not entities.get("court_id")
    ):
        return RouteDecision(route="rag_policy", entities=entities)
    if entities.get("court_id") or _has_any(stripped, AVAILABILITY_WORDS):
        return RouteDecision(route="get_court_availability", entities=entities)
    if _has_any(stripped, NOTIFICATION_WORDS) and _has_any(stripped, ("history",)):
        return RouteDecision(route="get_notification_history", entities=entities)
    if _has_any(stripped, TICKET_WORDS) and re.search(
        r"\b(current|previous|find|search|open)\b",
        stripped.lower(),
    ):
        if "refund" in stripped.lower():
            entities = {**entities, "topic": "refund"}
        return RouteDecision(route="search_previous_tickets", entities=entities)
    if _has_any(stripped, PAYMENT_WORDS) and (
        _has_any(stripped, ("status", "when", "delayed"))
    ):
        return RouteDecision(route="get_payment_status", entities=entities)
    return RouteDecision(route="rag_policy", entities=entities)
