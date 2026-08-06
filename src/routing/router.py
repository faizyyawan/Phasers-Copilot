"""Route support chat turns before retrieval or mock tool lookup."""

from __future__ import annotations

import json
import os
import re
import threading
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

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
SUPPORTED_MODEL_ROUTES = {
    "rag_policy",
    "get_booking_status",
    "get_payment_status",
    "get_notification_history",
    "search_previous_tickets",
    "get_court_availability",
    "human_escalation",
}
MODEL_ROUTE_ALIASES = {
    "rag_search": "rag_policy",
    "get_ticket_status": "search_previous_tickets",
}
IDENTIFIER_ENTITY_KEYS = {
    "booking_id",
    "payment_id",
    "notification_id",
    "ticket_id",
    "court_id",
}

_router_lock = threading.Lock()
_router_model: Any | None = None
_router_tokenizer: Any | None = None
_router_load_attempted = False


@dataclass(frozen=True)
class RouteDecision:
    """Routing result for one chat message."""

    route: str
    entities: dict[str, str] = field(default_factory=dict)
    handoff_reason: str | None = None
    backend: str = "rule_router"


def _router_enabled() -> bool:
    flag = os.getenv("ROUTER_USE_FINE_TUNED", "true").strip().lower()
    return flag not in {"0", "false", "no", "off"}


def _router_adapter_dir() -> Path:
    return Path(
        os.getenv(
            "ROUTER_ADAPTER_DIR",
            "artifacts/router-qlora-run1",
        )
    )


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


def _router_chat_template(message: str) -> list[dict[str, str]]:
    system_prompt = (
        "You are the query router for a RAG-based customer support system.\n\n"
        "Analyze the user's message and return only one valid JSON object.\n\n"
        "The JSON object must contain exactly these fields:\n"
        "- intent\n- entities\n- route\n- requires_escalation\n"
        "- rewrite\n- refusal_reason\n\n"
        "Do not answer the user's question.\n"
        "Do not include Markdown.\n"
        "Do not include explanations.\n"
        "Do not wrap the JSON in a code block."
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message},
    ]


def _extract_json_object(text: str) -> dict[str, Any] | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def _normalize_entity_value(key: str, value: object) -> str | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        text = str(value)
    elif isinstance(value, str):
        text = value.strip()
    else:
        return None
    if not text:
        return None
    if key in IDENTIFIER_ENTITY_KEYS:
        return text.upper()
    return text


def _normalize_model_entities(
    model_entities: object,
    message: str,
) -> dict[str, str]:
    entities = extract_entities(message)
    if not isinstance(model_entities, dict):
        return entities

    for key, value in model_entities.items():
        if not isinstance(key, str):
            continue
        normalized = _normalize_entity_value(key, value)
        if normalized is not None:
            entities[key] = normalized
    return entities


def _normalize_model_route(route: object) -> str | None:
    if not isinstance(route, str):
        return None
    normalized = MODEL_ROUTE_ALIASES.get(route.strip(), route.strip())
    if normalized in SUPPORTED_MODEL_ROUTES:
        return normalized
    return None


def _load_fine_tuned_router() -> tuple[Any, Any] | None:
    global _router_load_attempted, _router_model, _router_tokenizer

    if not _router_enabled():
        return None
    if _router_model is not None and _router_tokenizer is not None:
        return _router_model, _router_tokenizer
    if _router_load_attempted:
        return None

    with _router_lock:
        if _router_model is not None and _router_tokenizer is not None:
            return _router_model, _router_tokenizer
        if _router_load_attempted:
            return None

        adapter_dir = _router_adapter_dir()
        _router_load_attempted = True
        if not adapter_dir.exists():
            return None

        try:
            import torch
            from peft import AutoPeftModelForCausalLM
            from transformers import AutoTokenizer, BitsAndBytesConfig
        except ImportError:
            return None

        tokenizer = AutoTokenizer.from_pretrained(str(adapter_dir), trust_remote_code=False)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        load_kwargs: dict[str, Any] = {
            "trust_remote_code": False,
        }
        if torch.cuda.is_available():
            load_kwargs.update(
                {
                    "device_map": "auto",
                    "quantization_config": BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_compute_dtype=torch.float16,
                    ),
                    "dtype": torch.float16,
                }
            )
        else:
            load_kwargs.update(
                {
                    "device_map": None,
                    "dtype": torch.float32,
                    "low_cpu_mem_usage": True,
                }
            )

        model = AutoPeftModelForCausalLM.from_pretrained(
            str(adapter_dir),
            **load_kwargs,
        )
        model.eval()
        _router_model = model
        _router_tokenizer = tokenizer
        return model, tokenizer


def _route_with_fine_tuned_model(message: str) -> RouteDecision | None:
    loaded = _load_fine_tuned_router()
    if loaded is None:
        return None

    model, tokenizer = loaded
    try:
        import torch
    except ImportError:
        return None

    prompt_messages = _router_chat_template(message)
    prompt_text = tokenizer.apply_chat_template(
        prompt_messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    encoded = tokenizer(prompt_text, return_tensors="pt")
    encoded = {key: value.to(model.device) for key, value in encoded.items()}
    with torch.no_grad():
        generated = model.generate(
            **encoded,
            max_new_tokens=160,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    generated_tokens = generated[0][encoded["input_ids"].shape[1] :]
    raw_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
    parsed = _extract_json_object(raw_text)
    if not isinstance(parsed, dict):
        return None

    route = _normalize_model_route(parsed.get("route"))
    if route is None:
        return None

    handoff_reason = None
    if route == "human_escalation":
        refusal_reason = parsed.get("refusal_reason")
        if isinstance(refusal_reason, str) and refusal_reason.strip():
            handoff_reason = refusal_reason.strip()

        return RouteDecision(
            route=route,
            entities=_normalize_model_entities(parsed.get("entities"), message),
            handoff_reason=handoff_reason,
            backend="fine_tuned_router",
        )


def _route_with_rules(message: str, entities: dict[str, str]) -> RouteDecision:
    if entities.get("notification_id") or (
        entities.get("booking_id") and _has_any(message, NOTIFICATION_WORDS)
    ):
        return RouteDecision(route="get_notification_history", entities=entities)
    if entities.get("ticket_id") or (
        entities.get("booking_id") and _has_any(message, TICKET_WORDS)
    ):
        return RouteDecision(route="search_previous_tickets", entities=entities)
    if entities.get("payment_id") or (
        entities.get("booking_id") and _has_any(message, PAYMENT_WORDS)
    ):
        return RouteDecision(route="get_payment_status", entities=entities)
    if entities.get("booking_id") and _has_any(message, BOOKING_WORDS):
        return RouteDecision(route="get_booking_status", entities=entities)
    if (
        "owner" in message.lower()
        and _has_any(message, ("availability", "available"))
        and not entities.get("court_id")
    ):
        return RouteDecision(route="rag_policy", entities=entities)
    if entities.get("court_id") or _has_any(message, AVAILABILITY_WORDS):
        return RouteDecision(route="get_court_availability", entities=entities)
    if _has_any(message, NOTIFICATION_WORDS) and _has_any(message, ("history",)):
        return RouteDecision(route="get_notification_history", entities=entities)
    if _has_any(message, TICKET_WORDS) and re.search(
        r"\b(current|previous|find|search|open)\b",
        message.lower(),
    ):
        if "refund" in message.lower():
            entities = {**entities, "topic": "refund"}
        return RouteDecision(route="search_previous_tickets", entities=entities)
    if _has_any(message, PAYMENT_WORDS) and (
        _has_any(message, ("status", "when", "delayed"))
    ):
        return RouteDecision(route="get_payment_status", entities=entities)
    return RouteDecision(route="rag_policy", entities=entities)


def route_message(message: str) -> RouteDecision:
    """Choose safest route for one customer message."""
    stripped = message.strip()
    entities = extract_entities(stripped)
    reason = _handoff_reason(stripped)
    if reason:
        return RouteDecision(
            route="human_escalation",
            entities=entities,
            handoff_reason=reason,
            backend="safety_rule",
        )
    if GREETING_RE.fullmatch(stripped):
        return RouteDecision(route="greeting", entities=entities, backend="built_in_rule")
    if SMALLTALK_CLOSE_RE.fullmatch(stripped):
        return RouteDecision(route="smalltalk_close", entities=entities, backend="built_in_rule")
    lowered = stripped.lower()
    if re.search(r"\b(who|whoa|what)\s+(are|r|re)\s+(you|u)\b", lowered):
        return RouteDecision(route="bot_identity", entities=entities, backend="built_in_rule")
    if re.search(r"\bwhat\s+can\s+(you|u)\s+do\b", lowered):
        return RouteDecision(route="bot_identity", entities=entities, backend="built_in_rule")
    if re.search(r"\b(who|what)\s+(am|m)\s+(i|me)\b", lowered):
        return RouteDecision(route="user_identity", entities=entities, backend="built_in_rule")
    if not entities and not _has_any(stripped, SUPPORT_SCOPE_WORDS):
        return RouteDecision(route="out_of_scope", entities=entities, backend="built_in_rule")
    if (
        re.search(r"\bhow\s+do\s+i\b", lowered)
        or _has_any(stripped, ("change", "update", "edit", "replace", "modify"))
    ) and _has_any(
        stripped,
        ("phone", "number", "email", "password", "account"),
    ):
        return RouteDecision(route="account_update", entities=entities, backend="built_in_rule")

    model_decision = _route_with_fine_tuned_model(stripped)
    if model_decision is not None:
        return model_decision

    return _route_with_rules(stripped, entities)
