from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any


RAW_FILE = Path("data/router_raw.jsonl")
FALLBACK_RAW_FILE = Path("fine-tuning-data/sample-training-examples.jsonl")
TRAIN_FILE = Path("data/router_train.jsonl")
VALIDATION_FILE = Path("data/router_validation.jsonl")
TEST_FILE = Path("data/router_test.jsonl")

RANDOM_SEED = 42

REQUIRED_TARGET_FIELDS = {
    "intent",
    "entities",
    "route",
    "requires_escalation",
    "rewrite",
    "refusal_reason",
}

ALLOWED_ROUTES = {
    "rag_search",
    "get_booking_status",
    "get_payment_status",
    "get_notification_history",
    "get_court_availability",
    "search_previous_tickets",
    "human_escalation",
    "no_tool",
}

SYSTEM_PROMPT = """
You are the query router for a RAG-based customer support system.

Analyze the user's message and return only one valid JSON object.

The JSON object must contain exactly these fields:
- intent
- entities
- route
- requires_escalation
- rewrite
- refusal_reason

Do not answer the user's question.
Do not include Markdown.
Do not include explanations.
Do not wrap the JSON in a code block.
""".strip()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                example = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {exc}"
                ) from exc

            examples.append(example)

    if not examples:
        raise ValueError("The dataset is empty.")

    return examples


def validate_example(example: dict[str, Any], index: int) -> None:
    example_id = example.get("id", f"index-{index}")

    messages = example.get("messages")
    target = example.get("target")

    if not isinstance(messages, list) or not messages:
        raise ValueError(f"{example_id}: messages must be a non-empty list.")

    if not isinstance(target, dict):
        raise ValueError(f"{example_id}: target must be a JSON object.")

    target_fields = set(target)

    if target_fields != REQUIRED_TARGET_FIELDS:
        missing = REQUIRED_TARGET_FIELDS - target_fields
        extra = target_fields - REQUIRED_TARGET_FIELDS

        raise ValueError(
            f"{example_id}: incorrect target fields. "
            f"Missing={missing}, Extra={extra}"
        )

    if not isinstance(target["intent"], str) or not target["intent"].strip():
        raise ValueError(f"{example_id}: intent must be a non-empty string.")

    if not isinstance(target["entities"], dict):
        raise ValueError(f"{example_id}: entities must be an object.")

    if target["route"] not in ALLOWED_ROUTES:
        raise ValueError(
            f"{example_id}: unsupported route {target['route']!r}."
        )

    if not isinstance(target["requires_escalation"], bool):
        raise ValueError(
            f"{example_id}: requires_escalation must be true or false."
        )

    rewrite = target["rewrite"]
    refusal_reason = target["refusal_reason"]

    if rewrite is not None and not isinstance(rewrite, str):
        raise ValueError(f"{example_id}: rewrite must be a string or null.")

    if refusal_reason is not None and not isinstance(refusal_reason, str):
        raise ValueError(
            f"{example_id}: refusal_reason must be a string or null."
        )

    if target["route"] == "rag_search" and not rewrite:
        raise ValueError(
            f"{example_id}: rag_search requires a retrieval rewrite."
        )

    if target["route"] == "refusal" and not refusal_reason:
        raise ValueError(
            f"{example_id}: refusal requires a refusal_reason."
        )

    for message_index, message in enumerate(messages):
        if not isinstance(message, dict):
            raise ValueError(
                f"{example_id}: message {message_index} must be an object."
            )

        if message.get("role") not in {"system", "user", "assistant"}:
            raise ValueError(
                f"{example_id}: invalid role in message {message_index}."
            )

        content = message.get("content")

        if not isinstance(content, str) or not content.strip():
            raise ValueError(
                f"{example_id}: empty content in message {message_index}."
            )


def convert_example(example: dict[str, Any]) -> dict[str, Any]:
    original_messages = example["messages"]

    # Remove an existing system message because the training system
    # instruction should remain identical across the dataset.
    non_system_messages = [
        message
        for message in original_messages
        if message["role"] != "system"
    ]

    prompt = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        *non_system_messages,
    ]

    completion = [
        {
            "role": "assistant",
            "content": json.dumps(
                example["target"],
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=False,
            ),
        }
    ]

    return {
        "id": example["id"],
        "prompt": prompt,
        "completion": completion,
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(
                json.dumps(row, ensure_ascii=False) + "\n"
            )


def main() -> None:
    source_file = RAW_FILE if RAW_FILE.exists() else FALLBACK_RAW_FILE
    raw_examples = read_jsonl(source_file)

    for index, example in enumerate(raw_examples):
        validate_example(example, index)

    converted = [convert_example(example) for example in raw_examples]

    random.Random(RANDOM_SEED).shuffle(converted)

    total = len(converted)

    test_count = max(1, round(total * 0.10))
    validation_count = max(1, round(total * 0.10))

    test_examples = converted[:test_count]
    validation_examples = converted[
        test_count:test_count + validation_count
    ]
    train_examples = converted[test_count + validation_count:]

    if not train_examples:
        raise ValueError(
            "Not enough examples to create train, validation and test sets."
        )

    write_jsonl(TRAIN_FILE, train_examples)
    write_jsonl(VALIDATION_FILE, validation_examples)
    write_jsonl(TEST_FILE, test_examples)

    print(f"Source:     {source_file}")
    print(f"Total:      {total}")
    print(f"Training:   {len(train_examples)}")
    print(f"Validation: {len(validation_examples)}")
    print(f"Testing:    {len(test_examples)}")


if __name__ == "__main__":
    main()
    
