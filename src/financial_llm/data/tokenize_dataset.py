from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from transformers import AutoTokenizer

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from financial_llm.data.dataset import (  # noqa: E402
    PROMPT_TEMPLATE,
    load_examples,
)

DEFAULT_TOKENIZER = PROJECT_ROOT / "models" / "full_finetuned_gpt2"
DEFAULT_INPUT = PROJECT_ROOT / "data" / "processed"
MAX_LENGTH = 160


def tokenize_examples(
    examples: list[dict[str, str]], tokenizer: Any, max_length: int = MAX_LENGTH
) -> tuple[list[dict[str, list[int]]], dict[str, Any]]:
    if max_length < 2:
        raise ValueError("max_length must leave room for a prompt token and EOS.")
    if tokenizer.eos_token_id is None:
        raise ValueError("Tokenizer must define an EOS token.")

    encoded: list[dict[str, list[int]]] = []
    truncated_records: list[int] = []
    lengths: list[int] = []
    for index, example in enumerate(examples, start=1):
        prompt = PROMPT_TEMPLATE.format(instruction=example["instruction"].strip())
        text = prompt + example["response"].strip()
        prompt_ids = tokenizer(prompt, add_special_tokens=False)["input_ids"]
        full_ids = tokenizer(text, add_special_tokens=False)["input_ids"]
        if full_ids[: len(prompt_ids)] != prompt_ids:
            raise ValueError(
                f"Tokenizer prompt boundary mismatch at record {index}; "
                "refusing to mask the wrong target tokens."
            )
        if len(prompt_ids) >= max_length:
            raise ValueError(
                f"Prompt at record {index} uses {len(prompt_ids)} tokens, "
                f"not leaving response space in max_length={max_length}."
            )

        was_truncated = len(full_ids) + 1 > max_length
        token_ids = full_ids[: max_length - 1]
        token_ids.append(tokenizer.eos_token_id)
        labels = token_ids.copy()
        prompt_length = min(len(prompt_ids), len(token_ids) - 1)
        labels[:prompt_length] = [-100] * prompt_length
        if not any(label != -100 for label in labels):
            raise ValueError(f"Record {index} has no response tokens after masking.")
        if was_truncated:
            truncated_records.append(index)
        lengths.append(len(token_ids))
        encoded.append({
            "input_ids": token_ids,
            "attention_mask": [1] * len(token_ids),
            "labels": labels,
        })

    summary = {
        "record_count": len(encoded),
        "max_length": max_length,
        "min_tokens": min(lengths) if lengths else 0,
        "max_tokens": max(lengths) if lengths else 0,
        "mean_tokens": sum(lengths) / len(lengths) if lengths else 0,
        "truncated_record_numbers": truncated_records,
        "truncated_count": len(truncated_records),
    }
    return encoded, summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tokenize fixed train/validation/test partitions with response-only labels."
    )
    parser.add_argument("--tokenizer", type=Path, default=DEFAULT_TOKENIZER)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "data" / "processed" / "tokenized")
    parser.add_argument("--max-length", type=int, default=MAX_LENGTH)
    args = parser.parse_args()
    tokenizer = AutoTokenizer.from_pretrained(
        str(args.tokenizer),
        local_files_only=True,
    )
    tokenizer.pad_token = tokenizer.eos_token
    partitions = {}
    for name in ("train", "validation", "test"):
        source = args.input_dir / f"{name}.json"
        partitions[name] = tokenize_examples(
            load_examples(source), tokenizer, args.max_length
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, (examples, summary) in partitions.items():
        destination = args.output_dir / f"{name}.json"
        summary_path = args.output_dir / f"{name}_tokenization.json"
        for path in (destination, summary_path):
            if path.exists():
                raise FileExistsError(f"Refusing to overwrite existing file: {path}")
        with destination.open("w", encoding="utf-8", newline="\n") as file:
            json.dump(examples, file, ensure_ascii=False, indent=2)
            file.write("\n")
        with summary_path.open("w", encoding="utf-8", newline="\n") as file:
            json.dump(summary, file, ensure_ascii=False, indent=2)
            file.write("\n")
        print(f"{name}: {summary}")


if __name__ == "__main__":
    main()
