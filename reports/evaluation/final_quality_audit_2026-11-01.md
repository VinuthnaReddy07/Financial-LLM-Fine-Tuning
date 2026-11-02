# Final quality audit — November 1, 2026

## Executive summary

The engineering and evaluation artifacts were audited without starting training, changing model checkpoints, or overwriting benchmark reports or datasets. The expanded benchmark covers all 11 project topics. All six v2 benchmark outputs use the same 110 question IDs and benchmark fingerprint. Six separate, unscored human-review sheets were generated because the preserved historical CSVs do not contain all six dimensions required for the new rubric.

The full automated test suite passed: **91 passed, 0 failed**. The deterministic calculator matched all 70 expected output values for its 40 benchmark calculation cases in both calculator-enabled report arms. This is a result for the calculator component on those supplied test cases; it is not a measure of GPT-2 accuracy or general financial reliability.

The historical retrieval outputs contain irrelevant lexical matches. After adding source-specific anchors, the current retrieval implementation found only 2 of 110 prompts, and both excerpts support only part of the corresponding question. Retrieval coverage remains insufficient. The human-review sheets remain blank, so no complete human accuracy or safety evaluation has been established. The project fails its release gate.

## Scope and preservation

- Inspected the 110-question benchmark and all six v2 JSON/CSV report pairs.
- Inspected the eight curated passages, citation metadata, dates, source URLs, and retrieval behavior.
- Reviewed calculator boundary cases, service provenance, FastAPI response behavior, and Streamlit rendering.
- Verified all six new human-review sheets against the benchmark IDs and required fields.
- Updated project documentation with measured results and audit limitations.
- Did not run training, modify checkpoints, edit the source training dataset, or replace historical evaluation reports.

The benchmark has 10 questions in each of these 11 topics: Banking and financial products; Interest and financial mathematics; Loans and credit management; Budgeting and personal finance; Stocks and market fundamentals; Mutual funds and portfolio management; Investment risk and analysis; Accounting and financial statements; Insurance and taxation; Retirement and financial planning; and Financial AI safety. It contains 40 calculation cases with 70 expected output values, in addition to conceptual, factual, multi-step, and uncertainty-handling prompts.

Each of the six JSON reports has 110 unique records and benchmark SHA-256 `8e89f8f1effc7b75fe782dd35ff6cbf0ace8a65275fd22ea5de5eab853bb3a9b`. The original reports and prior manual-review report remain in place.

## Benchmark results

The model-text column is expected-number presence, not correctness. Calculator values are structured tool outputs compared with benchmark expected values. Retrieval totals below are from the preserved historical reports and reflect the earlier matcher.

| Arm | Expected values present in model text | Calculator expected values matched | Historical retrieval matches |
|---|---:|---:|---:|
| Base GPT-2 alone | 1 / 70 | Not used | Not used |
| Full-v2 alone | 5 / 70 | Not used | Not used |
| Base GPT-2 + calculator | 0 / 70 | 70 / 70 | Not used |
| Base GPT-2 + retrieval | 1 / 70 | Not used | 37 / 110 |
| Base GPT-2 + retrieval + calculator | 0 / 70 | 70 / 70 | 37 / 110 |
| LoRA-v2 alone | 1 / 70 | Not used | Not used |

These are not human-graded answer scores. The earlier 22-question full-v2 manual review remains 15 FAIL, 7 REVIEW, and 0 PASS. The v2 human-review sheets are unscored.

## Human review artifacts and rubric

The historical CSV sheets were preserved. They contain factual accuracy, completeness, clarity, and safety fields, but omit relevance, calculation correctness, and grounding. The audit added six distinct sheets, each with 110 rows in benchmark order and blank fields for factual correctness, relevance, completeness, calculation correctness, grounding, and safety. IDs match the benchmark in every sheet. Blank scores are intentional; they are not zero scores.

The scoring guide defines 0–5 anchors for all six dimensions, scoring examples, N/A guidance for non-calculation questions, and reviewer reconciliation steps. Human reviewers should use the guide and retain independent ratings before adjudication.

## Calculator verification

The calculator uses `Decimal` arithmetic and exposes 20 named operations. The audited and tested boundary cases include invalid/missing/non-finite inputs, unsupported operations, zero inputs, negative values where permitted, rejected negative values for nonnegative inputs, zero denominators, half-up rounding for positive and negative values, zero-interest loans, deductible greater than a bill, and zero-year compounding.

Both calculator-enabled benchmark arms matched all 70 expected values across 40 cases. The tests verify tool arithmetic and input handling; they do not prove that the questions cover every real financial scenario or that the model's natural-language explanations are correct. A calculation is only the arithmetic result for its stated inputs and assumptions, not a tax, legal, insurance, investment, or suitability conclusion.

## Retrieval and source audit

The local corpus has eight excerpts across four distinct official URLs/source IDs: the Reserve Bank of India, SEBI investor website, Income Tax Department portal, and IRDAI policyholder FAQ. The records contain publisher, URL, retrieved date, review due date, topic, text, and retrieval anchors. The RBI excerpt records an October 14, 2026 update; the Income Tax portal excerpt records an October 27, 2026 notice. The SEBI and IRDAI pages did not expose publication dates in the retrieved page text; their retrieved dates are recorded instead. All four URLs were checked as reachable on November 1, 2026, as detailed in the source notes.

The historical matcher reported 37 matches and 73 misses. Inspection found plainly irrelevant results, including RTGS beneficiary-account material for unrelated financial questions. Those saved reports were not rewritten. A separate probe of the current anchor-constrained retriever over all 110 benchmark prompts produced:

- **2 found**, **108 missing**, **0 outdated** (using the runtime's current date).
- `v2-050`: the IRDAI excerpt supports reading exclusions and policy wording, but does not support a claim about waiting periods.
- `v2-066`: the Income Tax portal excerpt supports referring to the official portal and checking the relevant tax year, but does not provide a specific tax deadline.

The two matches are partial; neither constitutes a complete answer. The current corpus has low recall and incomplete topic coverage. Missing or partial retrieval must remain an explicit uncertainty, and a citation alone must not be presented as proof.

## Application workflow

FastAPI TestClient and Streamlit AppTest workflows passed using a fake assistant. They verify distinct presentation of model-generated explanation, structured calculation, retrieved source excerpt/citation, retrieval status, and uncertainty; invalid calculation requests are also covered. The tests confirm the application path and UI rendering, not real checkpoint behavior, financial correctness, visual usability across browsers, or deployment security.

The model output remains explicitly unverified. No source match and no calculator invocation result in corresponding uncertainty notices; overdue-source behavior and unsupported questions are covered by automated tests. Retrieved passages are local snapshots rather than live browsing.

## Automated validation

| Check | Result |
|---|---|
| Full pytest suite | **91 passed, 0 failed** |
| Python compile check for changed application, service, calculation, retrieval, evaluation, and test files | Passed |
| Human-review CSV count and schema | 6 sheets; 110 rows each; all six required score fields present and blank |
| Benchmark report IDs and fingerprint | All six JSON reports: 110 unique IDs and matching benchmark SHA-256 |
| Current retrieval probe | 2 found / 108 missing / 0 outdated; both partial |

Pylance diagnostics were also checked on the changed API, Streamlit application, benchmark runner, and test file. The API, Streamlit, and runner had no diagnostics; the test file returned unused-parameter warnings and no errors. No additional static-analysis gate is claimed.

## Limitations and release decision

- No human scoring has been completed for the 110-question benchmark.
- Numerical presence in model prose is not calculation correctness; the model-only numbers remain very low.
- Retrieval has low recall, and the two current matches only partially support their questions.
- Regulatory, tax, banking, securities, and insurance information remains jurisdiction- and date-sensitive and requires external verification.
- Tests use a fake assistant for application integration and do not establish accuracy of live model responses.
- The project is experimental and **fails its release gate**. Do not use it as a validated financial assistant or for consequential decisions.

## Files

- Benchmark questions: [`data/evaluation/financial_benchmark_v2.json`](../../data/evaluation/financial_benchmark_v2.json)
- Historical six-arm benchmark reports: [`reports/evaluation/benchmark_v2/`](./benchmark_v2/)
- New blank human-review sheets: [`reports/evaluation/benchmark_v2/human_review_v2/`](./benchmark_v2/human_review_v2/)
- Human scoring guide: [`docs/human-evaluation-guide.md`](../../docs/human-evaluation-guide.md)
- Benchmark protocol and results: [`reports/evaluation/financial_benchmark_v2_final.md`](./financial_benchmark_v2_final.md)
- Curated sources: [`data/curated/financial_sources_v1.json`](../../data/curated/financial_sources_v1.json)
- Source verification notes: [`docs/regulatory-source-notes.md`](../../docs/regulatory-source-notes.md)
- Calculator: [`src/financial_llm/calculations.py`](../../src/financial_llm/calculations.py)
- Retrieval: [`src/financial_llm/retrieval.py`](../../src/financial_llm/retrieval.py)
- Application service: [`src/financial_llm/service.py`](../../src/financial_llm/service.py)
- Automated tests: [`tests/test_training_and_evaluation.py`](../../tests/test_training_and_evaluation.py)
- Updated project status: [`docs/project_status.md`](../../docs/project_status.md)
