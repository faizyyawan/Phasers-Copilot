"""Fine-tune a small chat model for router JSON generation."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import torch
from datasets import Dataset
from peft import LoraConfig, TaskType, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    set_seed,
)
from trl import SFTConfig, SFTTrainer


DEFAULT_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
DEFAULT_OUTPUT_DIR = Path("artifacts/router-qlora")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fine-tune router behavior with QLoRA or LoRA."
    )
    parser.add_argument(
        "--model-name",
        default=DEFAULT_MODEL,
        help="Base instruction model from Hugging Face.",
    )
    parser.add_argument(
        "--train-file",
        type=Path,
        default=Path("data/router_train.jsonl"),
    )
    parser.add_argument(
        "--validation-file",
        type=Path,
        default=Path("data/router_validation.jsonl"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-train-epochs", type=float, default=6.0)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--warmup-ratio", type=float, default=0.05)
    parser.add_argument("--logging-steps", type=int, default=5)
    parser.add_argument("--save-total-limit", type=int, default=2)
    parser.add_argument("--max-length", type=int, default=768)
    parser.add_argument("--max-steps", type=int, default=-1)
    parser.add_argument("--max-train-samples", type=int, default=None)
    parser.add_argument("--max-validation-samples", type=int, default=None)
    parser.add_argument("--per-device-train-batch-size", type=int, default=1)
    parser.add_argument("--per-device-eval-batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=8)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument(
        "--target-modules",
        nargs="+",
        default=["all-linear"],
        help="LoRA target modules. Use all-linear for broad small-model coverage.",
    )
    parser.add_argument(
        "--disable-4bit",
        action="store_true",
        help="Use regular LoRA instead of 4-bit QLoRA.",
    )
    parser.add_argument(
        "--use-fp16-trainer",
        action="store_true",
        help="Enable trainer AMP. Off by default for safer Windows CUDA runs.",
    )
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON in {path} line {line_number}: {exc}"
                ) from exc
            validate_row(row, path, line_number)
            rows.append(row)
    if not rows:
        raise ValueError(f"{path} is empty.")
    return rows


def validate_row(row: dict[str, Any], path: Path, line_number: int) -> None:
    if not isinstance(row.get("id"), str) or not row["id"].strip():
        raise ValueError(f"{path}:{line_number} missing string id.")
    prompt = row.get("prompt")
    completion = row.get("completion")
    if not isinstance(prompt, list) or not prompt:
        raise ValueError(f"{path}:{line_number} prompt must be non-empty list.")
    if not isinstance(completion, list) or not completion:
        raise ValueError(
            f"{path}:{line_number} completion must be non-empty list."
        )
    for field_name, messages in (("prompt", prompt), ("completion", completion)):
        for index, message in enumerate(messages):
            if not isinstance(message, dict):
                raise ValueError(
                    f"{path}:{line_number} {field_name}[{index}] not object."
                )
            if message.get("role") not in {"system", "user", "assistant"}:
                raise ValueError(
                    f"{path}:{line_number} {field_name}[{index}] bad role."
                )
            if not isinstance(message.get("content"), str) or not message["content"].strip():
                raise ValueError(
                    f"{path}:{line_number} {field_name}[{index}] empty content."
                )


def maybe_slice(rows: list[dict[str, Any]], limit: int | None) -> list[dict[str, Any]]:
    if limit is None:
        return rows
    return rows[:limit]


def build_dataset(rows: list[dict[str, Any]]) -> Dataset:
    return Dataset.from_list(rows)


def render_chat(
    tokenizer: AutoTokenizer,
    row: dict[str, Any],
) -> str:
    messages = row["prompt"] + row["completion"]
    if tokenizer.chat_template:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )
    lines: list[str] = []
    for message in messages:
        lines.append(f"{message['role'].upper()}: {message['content']}")
    return "\n\n".join(lines)


def render_dataset(
    dataset: Dataset,
    tokenizer: AutoTokenizer,
) -> Dataset:
    return dataset.map(
        lambda row: {"text": render_chat(tokenizer, row)},
        desc="Rendering chat examples",
    )


def build_quantization_config(disable_4bit: bool) -> BitsAndBytesConfig | None:
    if disable_4bit:
        return None
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )


def load_tokenizer(model_name: str) -> AutoTokenizer:
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def load_model(
    model_name: str,
    quantization_config: BitsAndBytesConfig | None,
) -> AutoModelForCausalLM:
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        trust_remote_code=False,
        quantization_config=quantization_config,
        dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )
    if quantization_config is not None:
        model = prepare_model_for_kbit_training(model)
    model.config.use_cache = False
    return model


def write_run_metadata(
    output_dir: Path,
    args: argparse.Namespace,
    train_rows: list[dict[str, Any]],
    validation_rows: list[dict[str, Any]],
    quantization_enabled: bool,
) -> None:
    metadata = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "model_name": args.model_name,
        "train_file": str(args.train_file),
        "validation_file": str(args.validation_file),
        "train_examples": len(train_rows),
        "validation_examples": len(validation_rows),
        "quantization": "4bit-nf4" if quantization_enabled else "disabled",
        "num_train_epochs": args.num_train_epochs,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "warmup_ratio": args.warmup_ratio,
        "max_length": args.max_length,
        "max_steps": args.max_steps,
        "per_device_train_batch_size": args.per_device_train_batch_size,
        "per_device_eval_batch_size": args.per_device_eval_batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "lora_r": args.lora_r,
        "lora_alpha": args.lora_alpha,
        "lora_dropout": args.lora_dropout,
        "target_modules": args.target_modules,
        "seed": args.seed,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = output_dir / "run_config.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def resolved_target_modules(target_modules: list[str]) -> str | list[str]:
    if target_modules == ["all-linear"]:
        return "all-linear"
    return target_modules


def main() -> None:
    args = parse_args()
    set_seed(args.seed)

    print("[1/6] Loading datasets...")
    train_rows = maybe_slice(read_jsonl(args.train_file), args.max_train_samples)
    validation_rows = maybe_slice(
        read_jsonl(args.validation_file),
        args.max_validation_samples,
    )
    train_dataset = build_dataset(train_rows)
    validation_dataset = build_dataset(validation_rows)
    print(f"Train examples: {len(train_rows)}")
    print(f"Validation examples: {len(validation_rows)}")

    print("[2/6] Loading tokenizer...")
    tokenizer = load_tokenizer(args.model_name)

    train_dataset = render_dataset(train_dataset, tokenizer)
    validation_dataset = render_dataset(validation_dataset, tokenizer)

    print("[3/6] Building model...")
    quantization_config = build_quantization_config(args.disable_4bit)
    model = load_model(args.model_name, quantization_config)

    print("[4/6] Configuring LoRA...")
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=resolved_target_modules(args.target_modules),
        bias="none",
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_run_metadata(
        output_dir=args.output_dir,
        args=args,
        train_rows=train_rows,
        validation_rows=validation_rows,
        quantization_enabled=quantization_config is not None,
    )

    training_args = SFTConfig(
        output_dir=str(args.output_dir),
        do_train=True,
        do_eval=True,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="steps",
        report_to="none",
        run_name="router-qlora",
        per_device_train_batch_size=args.per_device_train_batch_size,
        per_device_eval_batch_size=args.per_device_eval_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        num_train_epochs=args.num_train_epochs,
        max_steps=args.max_steps,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        warmup_ratio=args.warmup_ratio,
        logging_steps=args.logging_steps,
        save_total_limit=args.save_total_limit,
        seed=args.seed,
        max_length=args.max_length,
        gradient_checkpointing=True,
        fp16=args.use_fp16_trainer,
        bf16=False,
        save_only_model=True,
        load_best_model_at_end=False,
        dataset_text_field="text",
        packing=False,
    )

    print("[5/6] Building trainer...")
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        processing_class=tokenizer,
        peft_config=peft_config,
    )
    trainer.model.print_trainable_parameters()

    print("[6/6] Starting training...")
    trainer.train()
    trainer.save_model(str(args.output_dir))
    tokenizer.save_pretrained(str(args.output_dir))
    metrics = trainer.evaluate()
    metrics_path = args.output_dir / "final_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print("Training complete.")
    print(f"Adapter saved to: {args.output_dir}")
    print(f"Metrics saved to: {metrics_path}")


if __name__ == "__main__":
    main()
