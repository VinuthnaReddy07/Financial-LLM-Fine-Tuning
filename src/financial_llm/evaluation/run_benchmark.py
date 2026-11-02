from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from financial_llm.data.dataset import dataset_sha256, load_examples  # noqa: E402
from financial_llm.inference import FinancialAssistant  # noqa: E402
from financial_llm.retrieval import FinancialRetriever  # noqa: E402
from financial_llm.service import FinancialApplication  # noqa: E402


def load_benchmark(path: Path) -> list[dict[str, Any]]:
    items = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(items, list) or not items:
        raise ValueError(f"Benchmark must be a non-empty JSON list: {path}")
    required = {"id", "topic", "instruction", "required_points", "risk_flags"}
    identifiers: set[str] = set()
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict) or not required.issubset(item):
            raise ValueError(f"Benchmark record {index} is missing required fields.")
        if not all(
            isinstance(item[key], str) and item[key].strip()
            for key in ("id", "topic", "instruction")
        ):
            raise ValueError(f"Benchmark record {index} has an empty text field.")
        if item["id"] in identifiers:
            raise ValueError(f"Duplicate benchmark id: {item['id']}")
        identifiers.add(item["id"])
        if not isinstance(item["required_points"], list) or not isinstance(
            item["risk_flags"], list
        ):
            raise ValueError(f"Benchmark record {index} has invalid review criteria.")
        numbers = item.get("expected_numbers", [])
        if not isinstance(numbers, list) or any(
            not isinstance(number, (int, float)) for number in numbers
        ):
            raise ValueError(f"Benchmark record {index} has invalid expected numbers.")
        calculation_case = item.get("calculation_case")
        if calculation_case is not None:
            if (
                not isinstance(calculation_case, dict)
                or not isinstance(calculation_case.get("type"), str)
                or not isinstance(calculation_case.get("inputs"), dict)
                or not isinstance(calculation_case.get("expected_values"), dict)
            ):
                raise ValueError(f"Benchmark record {index} has an invalid calculation case.")
    return items


def _number_values(text: str) -> list[float]:
    return [
        float(value.replace(",", ""))
        for value in re.findall(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?", text)
    ]


def _numeric_check(
    response: str, expected: list[float], tolerance: float = 1e-8
) -> bool | None:
    if not expected:
        return None
    actual = _number_values(response)
    return all(
        any(abs(value - target) <= tolerance for value in actual)
        for target in expected
    )


def _numeric_coverage(
    response: str, expected_values: dict[str, str] | None
) -> dict[str, Any] | None:
    if not expected_values:
        return None
    actual = _number_values(response)
    expected: list[float] = []
    for target in expected_values.values():
        normalized = target.replace("%", "").replace(",", "")
        expected.append(float(normalized))
    matches = [
        any(abs(value - target) <= max(0.02, abs(target) * 1e-6) for value in actual)
        for target in expected
    ]
    return {
        "expected_values": len(expected),
        "matched_values": sum(matches),
        "all_values_present": all(matches),
    }


def _tool_check(
    calculation: dict[str, Any] | None,
    expected_values: dict[str, str] | None,
) -> dict[str, Any] | None:
    if not expected_values:
        return None
    if not calculation:
        return {
            "expected_values": len(expected_values),
            "matched_values": 0,
            "all_values_correct": False,
        }
    actual_values = calculation["values"]
    matched = 0
    for key, expected in expected_values.items():
        if key not in actual_values:
            continue
        try:
            actual_number = Decimal(actual_values[key].replace("%", "").replace(",", ""))
            expected_number = Decimal(expected.replace("%", "").replace(",", ""))
        except (InvalidOperation, AttributeError):
            continue
        if actual_number == expected_number:
            matched += 1
    return {
        "expected_values": len(expected_values),
        "matched_values": matched,
        "all_values_correct": matched == len(expected_values),
    }


def write_human_review_sheet(report: dict[str, Any], output_path: Path) -> None:
    fieldnames = (
        "id",
        "topic",
        "question_type",
        "instruction",
        "model_generated_answer",
        "required_points",
        "risk_flags",
        "calculation_case",
        "calculator_generated_result",
        "retrieved_source_evidence",
        "retrieval_status",
        "uncertainty",
        "factual_correctness_0_to_5",
        "relevance_0_to_5",
        "completeness_0_to_5",
        "calculation_correctness_0_to_5",
        "grounding_0_to_5",
        "safety_0_to_5",
        "reviewer_notes",
    )
    with output_path.open("x", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for result in report["results"]:
            writer.writerow(
                {
                    "id": result["id"],
                    "topic": result["topic"],
                    "question_type": result["question_type"],
                    "instruction": result["instruction"],
                    "model_generated_answer": result["response"],
                    "required_points": " | ".join(result["required_points"]),
                    "risk_flags": " | ".join(result["risk_flags"]),
                    "calculation_case": json.dumps(
                        result.get("calculation_case"),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "calculator_generated_result": json.dumps(
                        result.get("calculation"),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "retrieved_source_evidence": json.dumps(
                        result.get("retrieved_facts", []),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "retrieval_status": result.get("retrieval_status", "not_used"),
                    "uncertainty": " | ".join(result.get("uncertainty", [])),
                    "factual_correctness_0_to_5": "",
                    "relevance_0_to_5": "",
                    "completeness_0_to_5": "",
                    "calculation_correctness_0_to_5": "",
                    "grounding_0_to_5": "",
                    "safety_0_to_5": "",
                    "reviewer_notes": "",
                }
            )


def _similarity_scores(
    prompts: list[str], training_instructions: list[str]
) -> list[dict[str, Any]]:
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    vectors = vectorizer.fit_transform(training_instructions + prompts)
    training_vectors = vectors[: len(training_instructions)]
    prompt_vectors = vectors[len(training_instructions) :]
    matrix = cosine_similarity(prompt_vectors, training_vectors)
    results = []
    for row in matrix:
        best_index = int(row.argmax())
        results.append(
            {
                "max_tfidf_similarity": round(float(row[best_index]), 4),
                "closest_training_instruction": training_instructions[best_index],
            }
        )
    return results


def run_benchmark(
    model_path: str | Path,
    output_path: Path,
    benchmark_path: Path,
    training_path: Path,
    config_path: Path,
    base_model: str | None = None,
) -> dict[str, Any]:
    review_path = output_path.with_suffix(".csv")
    if output_path.exists() or review_path.exists():
        raise FileExistsError(
            f"Refusing to overwrite evaluation output: {output_path} or {review_path}"
        )
    benchmark = load_benchmark(benchmark_path)
    training_examples = load_examples(training_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    generation = config["generation"]
    assistant = FinancialAssistant(
        model_path=model_path,
        base_model=base_model,
        max_new_tokens=int(generation["max_new_tokens"]),
        repetition_penalty=float(generation["repetition_penalty"]),
        no_repeat_ngram_size=int(generation["no_repeat_ngram_size"]),
    )
    similarities = _similarity_scores(
        [item["instruction"] for item in benchmark],
        [item["instruction"] for item in training_examples],
    )
    results = []
    for item, similarity in zip(benchmark, similarities, strict=True):
        response = assistant.generate(item["instruction"])
        results.append(
            {
                **item,
                "response": response,
                **similarity,
                "numeric_check": _numeric_check(
                    response, item.get("expected_numbers", [])
                ),
            }
        )

    report = {
        "benchmark": str(benchmark_path),
        "benchmark_records": len(results),
        "benchmark_sha256": dataset_sha256(benchmark_path),
        "model_path": str(model_path),
        "base_model": base_model,
        "training_split_sha256": dataset_sha256(training_path),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "generation_config": generation,
        "automated_scores_are_not_a_quality_claim": True,
        "results": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
        file.write("\n")
    write_human_review_sheet(report, review_path)
    return report


def run_comparison_arm(
    *,
    arm: str,
    model_path: str | Path,
    output_path: Path,
    benchmark_path: Path,
    training_path: Path,
    config_path: Path,
    base_model: str | None = None,
) -> dict[str, Any]:
    review_path = output_path.with_suffix(".csv")
    if output_path.exists() or review_path.exists():
        raise FileExistsError(
            f"Refusing to overwrite evaluation output: {output_path} or {review_path}"
        )
    if arm not in {
        "base",
        "full",
        "lora",
        "calculator",
        "retrieval",
        "retrieval_calculator",
    }:
        raise ValueError(f"Unsupported comparison arm: {arm}")

    benchmark = load_benchmark(benchmark_path)
    training_examples = load_examples(training_path)
    training_instructions = [item["instruction"] for item in training_examples]
    normalized_training = {
        " ".join(instruction.casefold().split())
        for instruction in training_instructions
    }
    config = json.loads(config_path.read_text(encoding="utf-8"))
    generation = config["generation"]
    assistant = FinancialAssistant(
        model_path=model_path,
        base_model=base_model,
        max_new_tokens=int(generation["max_new_tokens"]),
        repetition_penalty=float(generation["repetition_penalty"]),
        no_repeat_ngram_size=int(generation["no_repeat_ngram_size"]),
    )
    with_tools = arm in {"calculator", "retrieval", "retrieval_calculator"}
    use_calculator = arm in {"calculator", "retrieval_calculator"}
    use_retrieval = arm in {"retrieval", "retrieval_calculator"}
    application = (
        FinancialApplication(
            assistant,
            retriever=FinancialRetriever(
                PROJECT_ROOT / "data" / "curated" / "financial_sources_v1.json"
            ),
        )
        if with_tools
        else None
    )
    similarities = _similarity_scores(
        [item["instruction"] for item in benchmark],
        training_instructions,
    )
    results: list[dict[str, Any]] = []
    for item, similarity in zip(benchmark, similarities, strict=True):
        instruction = item["instruction"]
        normalized = " ".join(instruction.casefold().split())
        exact_train_duplicate = normalized in normalized_training
        if application is None:
            response = assistant.generate(instruction)
            application_result: dict[str, Any] = {
                "retrieved_facts": [],
                "retrieval_status": "not_used",
                "calculation": None,
                "uncertainty": [],
            }
        else:
            calculation_case = item.get("calculation_case")
            use_case_calculation = use_calculator and calculation_case is not None
            application_result = application.respond(
                instruction,
                calculation_type=(
                    calculation_case["type"] if use_case_calculation else None
                ),
                calculation_inputs=(
                    calculation_case["inputs"] if use_case_calculation else None
                ),
                use_retrieval=use_retrieval,
            )
            response = application_result["model_explanation"]

        calculation_case = item.get("calculation_case")
        expected_values = (
            calculation_case["expected_values"] if calculation_case else None
        )
        calculation = application_result["calculation"]
        numeric_coverage = _numeric_coverage(response, expected_values)
        tool_check = (
            _tool_check(calculation, expected_values)
            if use_calculator and expected_values is not None
            else None
        )
        result = {
            **item,
            "response": response,
            **similarity,
            "exact_training_prompt_duplicate": exact_train_duplicate,
            "model_numeric_coverage": numeric_coverage,
            "tool_calculation_check": tool_check,
            "retrieved_facts": application_result["retrieved_facts"],
            "retrieval_status": application_result["retrieval_status"],
            "calculation": calculation,
            "uncertainty": application_result["uncertainty"],
        }
        results.append(result)

    numeric_rows = [
        result for result in results if result["model_numeric_coverage"] is not None
    ]
    tool_rows = [
        result for result in results if result["tool_calculation_check"] is not None
    ]
    retrieval_rows = [
        result
        for result in results
        if result["retrieval_status"] not in {"not_used", "disabled"}
    ]
    topic_metrics: dict[str, Any] = {}
    for topic in sorted({result["topic"] for result in results}):
        topic_results = [result for result in results if result["topic"] == topic]
        topic_metrics[topic] = {
            "cases": len(topic_results),
            "calculation_cases": sum(
                result["calculation_case"] is not None
                for result in topic_results
            ),
            "retrieval_found": sum(
                result["retrieval_status"] == "found"
                for result in topic_results
            ),
        }
    report = {
        "arm": arm,
        "benchmark": str(benchmark_path),
        "benchmark_sha256": dataset_sha256(benchmark_path),
        "benchmark_records": len(results),
        "model_path": str(model_path),
        "base_model": base_model,
        "training_split_sha256": dataset_sha256(training_path),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "generation_config": generation,
        "automated_metrics_are_not_human_accuracy_scores": True,
        "summary": {
            "exact_prompt_duplicates": sum(
                result["exact_training_prompt_duplicate"] for result in results
            ),
            "prompts_similarity_at_least_0_8": sum(
                result["max_tfidf_similarity"] >= 0.8 for result in results
            ),
            "max_training_prompt_similarity": max(
                result["max_tfidf_similarity"] for result in results
            ),
            "numeric_model_values_matched": sum(
                score["matched_values"]
                for result in numeric_rows
                if (score := result["model_numeric_coverage"]) is not None
            ),
            "numeric_model_values_expected": sum(
                score["expected_values"]
                for result in numeric_rows
                if (score := result["model_numeric_coverage"]) is not None
            ),
            "tool_values_matched": (
                sum(
                    score["matched_values"]
                    for result in tool_rows
                    if (score := result["tool_calculation_check"]) is not None
                )
                if use_calculator
                else None
            ),
            "tool_values_expected": (
                sum(
                    score["expected_values"]
                    for result in tool_rows
                    if (score := result["tool_calculation_check"]) is not None
                )
                if use_calculator
                else None
            ),
            "retrieval_queries": len(retrieval_rows),
            "retrieval_found": sum(
                result["retrieval_status"] == "found" for result in retrieval_rows
            ),
            "retrieval_missing": sum(
                result["retrieval_status"] == "missing" for result in retrieval_rows
            ),
            "retrieval_outdated": sum(
                result["retrieval_status"] == "outdated" for result in retrieval_rows
            ),
        },
        "topic_metrics": topic_metrics,
        "question_type_metrics": {
            question_type: {
                "cases": sum(
                    result["question_type"] == question_type for result in results
                ),
                "calculation_cases": sum(
                    result["question_type"] == question_type
                    and result["calculation_case"] is not None
                    for result in results
                ),
            }
            for question_type in sorted(
                {result["question_type"] for result in results}
            )
        },
        "results": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
        file.write("\n")
    write_human_review_sheet(report, review_path)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate model outputs and a manual review sheet."
    )
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--base-model", default=None)
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--training-split",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "train.json",
    )
    parser.add_argument(
        "--config", type=Path, default=PROJECT_ROOT / "configs" / "training.json"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--arm",
        choices=(
            "base",
            "full",
            "lora",
            "calculator",
            "retrieval",
            "retrieval_calculator",
        ),
    )
    args = parser.parse_args()
    benchmark_path = args.benchmark or (
        PROJECT_ROOT
        / "data"
        / "evaluation"
        / (
            "financial_benchmark_v2.json"
            if args.arm
            else "manual_benchmark_v1.json"
        )
    )
    if args.arm:
        report = run_comparison_arm(
            arm=args.arm,
            model_path=args.model_path,
            base_model=args.base_model,
            output_path=args.output,
            benchmark_path=benchmark_path,
            training_path=args.training_split,
            config_path=args.config,
        )
        print(json.dumps(report["summary"], indent=2))
        return
    report = run_benchmark(
        model_path=args.model_path,
        base_model=args.base_model,
        output_path=args.output,
        benchmark_path=benchmark_path,
        training_path=args.training_split,
        config_path=args.config,
    )
    print(f"Generated {report['benchmark_records']} responses at {args.output}")


if __name__ == "__main__":
    main()
