from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from financial_llm.data.dataset import (  # noqa: E402
    dataset_sha256,
    find_exact_instruction_duplicates,
    load_examples,
    normalize_text,
)

DEFAULT_SOURCE = PROJECT_ROOT / "data" / "validated" / "financial_dataset_v1.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "processed"
SIMILARITY_THRESHOLD = 0.80
RANDOM_SEED = 42


def near_duplicate_groups(
    examples: list[dict[str, str]], threshold: float = SIMILARITY_THRESHOLD
) -> list[int]:
    parent = list(range(len(examples)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(first: int, second: int) -> None:
        root_first = find(first)
        root_second = find(second)
        if root_first != root_second:
            parent[root_second] = root_first

    exact: dict[str, int] = {}
    for index, example in enumerate(examples):
        instruction = normalize_text(example["instruction"])
        if instruction in exact:
            union(index, exact[instruction])
        else:
            exact[instruction] = index

    if len(examples) > 1:
        matrix = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            stop_words="english",
        ).fit_transform([item["instruction"] for item in examples])
        similarities = cosine_similarity(matrix)
        for first in range(len(examples)):
            for second in range(first + 1, len(examples)):
                if similarities[first, second] >= threshold:
                    union(first, second)

    roots: dict[int, int] = {}
    return [roots.setdefault(find(index), len(roots)) for index in range(len(examples))]


def split_examples(
    examples: list[dict[str, str]], seed: int = RANDOM_SEED
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], dict[str, Any]]:
    duplicates = find_exact_instruction_duplicates(examples)
    if duplicates:
        raise ValueError(f"Exact duplicate instructions found: {duplicates}")
    groups = near_duplicate_groups(examples)
    indices = list(range(len(examples)))

    first_split = GroupShuffleSplit(n_splits=1, test_size=0.10, random_state=seed)
    train_validation_indexes, test_indexes = next(
        first_split.split(indices, groups=groups)
    )
    train_validation_groups = [groups[index] for index in train_validation_indexes]
    second_split = GroupShuffleSplit(
        n_splits=1,
        test_size=1 / 9,
        random_state=seed + 1,
    )
    train_indexes_local, validation_indexes_local = next(
        second_split.split(train_validation_indexes, groups=train_validation_groups)
    )
    train_indexes = [train_validation_indexes[index] for index in train_indexes_local]
    validation_indexes = [
        train_validation_indexes[index] for index in validation_indexes_local
    ]

    partitions = [
        [examples[index] for index in train_indexes],
        [examples[index] for index in validation_indexes],
        [examples[index] for index in test_indexes],
    ]
    partition_groups = [
        {groups[index] for index in partition_indexes}
        for partition_indexes in (train_indexes, validation_indexes, test_indexes)
    ]
    if (
        partition_groups[0] & partition_groups[1]
        or partition_groups[0] & partition_groups[2]
        or partition_groups[1] & partition_groups[2]
    ):
        raise RuntimeError("Near-duplicate group leakage detected after split.")

    metadata = {
        "seed": seed,
        "similarity_threshold": SIMILARITY_THRESHOLD,
        "group_count": len(set(groups)),
        "split_sizes": {
            "train": len(partitions[0]),
            "validation": len(partitions[1]),
            "test": len(partitions[2]),
        },
        "group_counts": {
            "train": len(partition_groups[0]),
            "validation": len(partition_groups[1]),
            "test": len(partition_groups[2]),
        },
    }
    return partitions[0], partitions[1], partitions[2], metadata


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create deterministic, similarity-grouped train/validation/test splits."
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    args = parser.parse_args()

    train, validation, test, metadata = split_examples(
        load_examples(args.source), seed=args.seed
    )
    output_paths = {
        "train": args.output_dir / "train.json",
        "validation": args.output_dir / "validation.json",
        "test": args.output_dir / "test.json",
        "metadata": args.output_dir / "split_metadata.json",
    }
    for output_path in output_paths.values():
        if output_path.exists():
            raise FileExistsError(f"Refusing to overwrite existing file: {output_path}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, examples in (
        ("train", train),
        ("validation", validation),
        ("test", test),
    ):
        with output_paths[name].open("w", encoding="utf-8", newline="\n") as file:
            json.dump(examples, file, ensure_ascii=False, indent=2)
            file.write("\n")
    metadata["dataset_sha256"] = dataset_sha256(args.source)
    metadata["source"] = str(args.source.relative_to(PROJECT_ROOT))
    with output_paths["metadata"].open("w", encoding="utf-8", newline="\n") as file:
        json.dump(metadata, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
