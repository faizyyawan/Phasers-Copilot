# QLoRA Fine-Tuning Plan

## What LoRA Is

LoRA trains small adapter matrices while keeping most base model weights frozen. It is useful when you want to adapt behavior without full model fine-tuning.

## What QLoRA Is

QLoRA combines LoRA adapters with a quantized base model, often using 4-bit weights. This reduces memory requirements and makes small experiments more accessible.

## Why QLoRA Is Useful Here

QLoRA can teach the model support-agent behavior such as classification, extraction, routing, escalation, refusal, and structured JSON output.

## What It Should Train

1. Intent classification
2. Entity extraction
3. Tool selection
4. Escalation prediction
5. Structured JSON generation

## What It Should Not Train

Do not train changing business facts such as refund timelines, advance percentages, or cancellation windows into the model. Business-policy facts must remain in RAG.

## Dataset Creation

Use reviewed examples with input, expected JSON output, labels, and reviewer notes. Keep the dataset small at first and inspect every example manually.

## Data Quality

Prefer consistent labels over large volume. Remove contradictions, private data, duplicated near-identical examples, and policy facts that should come from documents.

## Chat Templates

Use the chat template expected by the chosen instruction model. The same formatting should be used during training and inference.

## Splits

Use train, validation, and test splits. Keep similar examples together in one split to avoid leakage.

## Quantization and NF4

Quantization reduces precision to save memory. NF4 is a common 4-bit format used in QLoRA. Test whether quantization affects behavior on your validation set.

## PEFT, TRL, Transformers, and bitsandbytes

- Transformers loads the base model and tokenizer.
- bitsandbytes enables 4-bit quantized loading.
- PEFT defines and saves LoRA adapters.
- TRL provides supervised fine-tuning utilities.

## Model Choice

Begin with a small 1.5B-3B instruction model. Do not make one specific model mandatory; compare availability, license, hardware fit, tokenizer behavior, and structured-output reliability.

## Checkpointing and Adapter Saving

Save adapter checkpoints with dataset version, label schema version, base model name, training arguments, and evaluation metrics.

## Evaluation

Compare the base model and adapter on held-out behavior tests. Measure intent accuracy, entity extraction accuracy, tool-selection accuracy, escalation accuracy, refusal accuracy, and valid JSON rate.

## Overfitting and Leakage

If training accuracy improves but validation does not, suspect overfitting. If held-out performance looks suspiciously high, audit for leakage.

