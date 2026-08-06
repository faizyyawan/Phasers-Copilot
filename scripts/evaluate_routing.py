"""Evaluate the rule-based router against routing-test-cases.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.routing.router import route_message

DATASET = ROOT / "evaluation-data" / "routing-test-cases.json"

ROUTE_TO_EVAL_ROUTE = {
    "greeting": "no_tool",
    "smalltalk_close": "no_tool",
    "rag_policy": "rag_search",
    "human_escalation": "human_escalation",
    "get_booking_status": "get_booking_status",
    "get_payment_status": "get_payment_status",
    "get_notification_history": "get_notification_history",
    "search_previous_tickets": "search_previous_tickets",
    "get_court_availability": "get_court_availability",
}


def main() -> None:
    """Run routing dataset checks and print a compact report."""
    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    failures: list[str] = []

    for case in cases:
        decision = route_message(case["question"])
        actual_route = ROUTE_TO_EVAL_ROUTE.get(decision.route, decision.route)
        actual_entities = dict(decision.entities)
        if decision.handoff_reason:
            actual_entities["reason"] = decision.handoff_reason

        if actual_route != case["expected_route"]:
            failures.append(
                f"{case['id']}: route {actual_route} != {case['expected_route']}"
            )
            continue

        for key, expected_value in case["expected_entities"].items():
            if str(actual_entities.get(key)) != str(expected_value):
                failures.append(
                    f"{case['id']}: entity {key}={actual_entities.get(key)} "
                    f"!= {expected_value}"
                )

    if failures:
        print(f"Routing evaluation failed: {len(failures)} / {len(cases)}")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print(f"Routing evaluation passed: {len(cases)} / {len(cases)}")


if __name__ == "__main__":
    main()
