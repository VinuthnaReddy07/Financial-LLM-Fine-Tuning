from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


PROMPT_TEMPLATE = "### Instruction:\n{instruction}\n\n### Response:\n"
REQUIRED_FIELDS = {"instruction", "response"}


def load_examples(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as file:
        examples: Any = json.load(file)
    if not isinstance(examples, list):
        raise ValueError(f"Dataset must be a JSON list: {path}")
    validate_examples(examples)
    return examples


def validate_examples(examples: list[dict[str, Any]]) -> None:
    for index, example in enumerate(examples, start=1):
        if not isinstance(example, dict) or set(example) != REQUIRED_FIELDS:
            raise ValueError(
                f"Record {index} must contain exactly instruction and response."
            )
        for field in REQUIRED_FIELDS:
            value = example[field]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Record {index} has an empty or non-string {field}."
                )


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def find_exact_instruction_duplicates(
    examples: list[dict[str, str]],
) -> dict[str, list[int]]:
    positions: dict[str, list[int]] = {}
    for index, example in enumerate(examples, start=1):
        positions.setdefault(normalize_text(example["instruction"]), []).append(index)
    return {text: indexes for text, indexes in positions.items() if len(indexes) > 1}


def prompt_for(instruction: str) -> str:
    return PROMPT_TEMPLATE.format(instruction=instruction.strip())


def dataset_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
