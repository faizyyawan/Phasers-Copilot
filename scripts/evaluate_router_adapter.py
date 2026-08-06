"""Evaluate base or adapter model on router JSON outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import torch
from peft import AutoPeftModelForCausalLM
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)


DEFAULT_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate router adapter or base model."
    )
    parser.add_argument(
        "--model-name",
        default=DEFAULT_MODEL,
        help="Base model name. Used directly when --adapter-dir is omitted.",
    )
    parser.add_argument(
        "--adapter-dir",
        type=Path,
        default=None,
        help="Adapter directory from train_router_qlora.py.",
    )
    parser.add_argument(
        "--test-file",
        type=Path,
        default=Path("data/router_test.jsonl"),
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=Path("artifacts/router-qlora/test_predictions.json"),
    )
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--max-new-tokens", type=int, default=160)
    parser.add_argument(
        "--disable-4bit",
        action="store_true",
        help="Disable 4-bit loading for evaluation.",
    )
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON in {path} line {line_number}: {exc}"
                ) from exc
    if not rows:
        raise ValueError(f"{path} is empty.")
    return rows


def render_prompt(
    tokenizer: AutoTokenizer,
    row: dict[str, Any],
) -> str:
    messages = row["prompt"]
    if tokenizer.chat_template:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
    lines: list[str] = []
    for message in messages:
        lines.append(f"{message['role'].upper()}: {message['content']}")
    lines.append("ASSISTANT:")
    return "\n\n".join(lines)


def maybe_extract_json(text: str) -> dict[str, Any] | None:
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


def expected_target(row: dict[str, Any]) -> dict[str, Any]:
    content = row["completion"][0]["content"]
    return json.loads(content)


def build_quantization_config(disable_4bit: bool) -> BitsAndBytesConfig | None:
    if disable_4bit:
        return None
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )


def load_model_and_tokenizer(
    model_name: str,
    adapter_dir: Path | None,
    disable_4bit: bool,
):
    quantization_config = build_quantization_config(disable_4bit)
    tokenizer_source = str(adapter_dir) if adapter_dir else model_name
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_source, trust_remote_code=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    common_kwargs = {
        "device_map": "auto",
        "trust_remote_code": False,
        "quantization_config": quantization_config,
        "dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
    }
    if adapter_dir:
        model = AutoPeftModelForCausalLM.from_pretrained(
            str(adapter_dir),
            **common_kwargs,
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            **common_kwargs,
        )
    model.eval()
    return model, tokenizer


def main() -> None:
    args = parse_args()
    rows = read_jsonl(args.test_file)
    if args.max_samples is not None:
        rows = rows[: args.max_samples]

    print("Loading model for evaluation...")
    model, tokenizer = load_model_and_tokenizer(
        model_name=args.model_name,
        adapter_dir=args.adapter_dir,
        disable_4bit=args.disable_4bit,
    )

    total = len(rows)
    valid_json = 0
    exact_match = 0
    route_match = 0
    intent_match = 0
    escalation_match = 0
    predictions: list[dict[str, Any]] = []

    for index, row in enumerate(rows, start=1):
        prompt_text = render_prompt(tokenizer, row)
        encoded = tokenizer(
            prompt_text,
            return_tensors="pt",
        )
        encoded = {key: value.to(model.device) for key, value in encoded.items()}
        with torch.no_grad():
            generated = model.generate(
                **encoded,
                max_new_tokens=args.max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        generated_tokens = generated[0][encoded["input_ids"].shape[1] :]
        raw_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        parsed = maybe_extract_json(raw_text)
        expected = expected_target(row)

        if parsed is not None:
            valid_json += 1
            if parsed == expected:
                exact_match += 1
            if parsed.get("route") == expected.get("route"):
                route_match += 1
            if parsed.get("intent") == expected.get("intent"):
                intent_match += 1
            if parsed.get("requires_escalation") == expected.get("requires_escalation"):
                escalation_match += 1

        predictions.append(
            {
                "id": row["id"],
                "raw_output": raw_text,
                "parsed_output": parsed,
                "expected": expected,
            }
        )
        print(f"[{index}/{total}] {row['id']} done")

    metrics = {
        "total": total,
        "valid_json_rate": valid_json / total if total else 0.0,
        "exact_match_rate": exact_match / total if total else 0.0,
        "route_accuracy": route_match / total if total else 0.0,
        "intent_accuracy": intent_match / total if total else 0.0,
        "escalation_accuracy": escalation_match / total if total else 0.0,
        "adapter_dir": str(args.adapter_dir) if args.adapter_dir else None,
        "model_name": args.model_name,
    }

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(
        json.dumps(
            {
                "metrics": metrics,
                "predictions": predictions,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(json.dumps(metrics, indent=2))
    print(f"Saved predictions to {args.output_file}")


if __name__ == "__main__":
    main()
