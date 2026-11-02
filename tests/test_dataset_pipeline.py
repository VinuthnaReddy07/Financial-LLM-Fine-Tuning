from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from financial_llm.data.dataset import (  # noqa: E402
    find_exact_instruction_duplicates,
    prompt_for,
    validate_examples,
)
from financial_llm.data.split_dataset import near_duplicate_groups, split_examples  # noqa: E402
from financial_llm.data.tokenize_dataset import tokenize_examples  # noqa: E402


class TinyTokenizer:
    eos_token_id = 99

    def __call__(self, text: str, add_special_tokens: bool = False) -> dict[str, list[int]]:
        assert not add_special_tokens
        return {"input_ids": [ord(char) for char in text]}


def test_schema_requires_only_nonempty_instruction_and_response() -> None:
    validate_examples([{"instruction": "Question", "response": "Answer"}])
    with pytest.raises(ValueError, match="exactly"):
        validate_examples([{"instruction": "Question", "response": "Answer", "topic": "x"}])
    with pytest.raises(ValueError, match="empty or non-string"):
        validate_examples([{"instruction": " ", "response": "Answer"}])


def test_exact_duplicate_detection_normalizes_case_and_whitespace() -> None:
    examples = [
        {"instruction": "What is APR?", "response": "One."},
        {"instruction": " what is apr? ", "response": "Two."},
    ]
    assert find_exact_instruction_duplicates(examples) == {
        "what is apr?": [1, 2]
    }


def test_prompt_format_matches_training_template() -> None:
    assert prompt_for("  Explain risk. ") == (
        "### Instruction:\nExplain risk.\n\n### Response:\n"
    )


def test_tokenization_masks_prompt_and_keeps_eos_as_target() -> None:
    tokenized, metadata = tokenize_examples(
        [{"instruction": "Q", "response": "A"}], TinyTokenizer(), max_length=100
    )
    row = tokenized[0]
    prompt_length = len(TinyTokenizer()(
        prompt_for("Q"), add_special_tokens=False
    )["input_ids"])
    assert row["input_ids"][-1] == TinyTokenizer.eos_token_id
    assert row["labels"][:prompt_length] == [-100] * prompt_length
    assert row["labels"][-1] == TinyTokenizer.eos_token_id
    assert metadata["truncated_count"] == 0


def test_tokenization_preserves_eos_when_response_is_truncated() -> None:
    tokenized, metadata = tokenize_examples(
        [{"instruction": "Q", "response": "A" * 20}],
        TinyTokenizer(),
        max_length=50,
    )
    assert len(tokenized[0]["input_ids"]) == 50
    assert tokenized[0]["input_ids"][-1] == TinyTokenizer.eos_token_id
    assert metadata["truncated_record_numbers"] == [1]


def test_tokenization_refuses_a_truncated_prompt() -> None:
    with pytest.raises(ValueError, match="Prompt"):
        tokenize_examples(
            [{"instruction": "A" * 30, "response": "Answer"}],
            TinyTokenizer(),
            max_length=20,
        )


def test_near_duplicate_groups_do_not_split_question_variants() -> None:
    rows = [
        {"instruction": "What is compound interest?", "response": "A"},
        {"instruction": "Explain compound interest.", "response": "B"},
        {"instruction": "How does a credit score work?", "response": "C"},
    ]
    groups = near_duplicate_groups(rows, threshold=0.45)
    assert groups[0] == groups[1]
    assert groups[0] != groups[2]


def test_split_keeps_all_examples_and_groups_separate() -> None:
    examples = [
        {"instruction": f"concept{index} subject{index}.", "response": "Answer"}
        for index in range(50)
    ]
    train, validation, test, metadata = split_examples(examples)
    assert len(train) + len(validation) + len(test) == len(examples)
    assert all((part) for part in (train, validation, test))
    assert metadata["group_count"] == len(examples)
    assert len({
        item["instruction"]
        for part in (train, validation, test)
        for item in part
    }) == len(examples)


def test_canonical_dataset_contains_only_valid_records() -> None:
    path = ROOT / "data" / "validated" / "financial_dataset_v1.json"
    if not path.exists():
        pytest.skip("Canonical dataset has not been built.")
    examples = json.loads(path.read_text(encoding="utf-8"))
    validate_examples(examples)
    assert len(examples) == 298
