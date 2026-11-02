from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from financial_llm.evaluation.run_benchmark import write_human_review_sheet

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REPORT_DIR = PROJECT_ROOT / "reports" / "evaluation" / "benchmark_v2"
DEFAULT_OUTPUT_DIR = DEFAULT_REPORT_DIR / "human_review_v2"


def build_review_sheets(report_dir: Path, output_dir: Path) -> list[Path]:
    report_paths = sorted(
        path for path in report_dir.glob("*.json") if path.is_file()
    )
    if not report_paths:
        raise FileNotFoundError(f"No JSON evaluation reports found in {report_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    for report_path in report_paths:
        report: dict[str, Any] = json.loads(report_path.read_text(encoding="utf-8"))
        results = report.get("results")
        if not isinstance(results, list) or len(results) != report.get(
            "benchmark_records"
        ):
            raise ValueError(f"Invalid evaluation result list in {report_path}")
        output_path = output_dir / f"{report_path.stem}.human-review.csv"
        write_human_review_sheet(report, output_path)
        created.append(output_path)
    return created


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build separate human-review sheets without changing reports."
    )
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    paths = build_review_sheets(args.reports_dir, args.output_dir)
    print(json.dumps({"created": [str(path) for path in paths]}, indent=2))


if __name__ == "__main__":
    main()
