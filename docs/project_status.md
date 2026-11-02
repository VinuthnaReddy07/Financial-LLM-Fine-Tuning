# Project status

## Completed

- Preserved source datasets, legacy training data, model checkpoints, and prior reports; the original 305-example dataset was not modified.
- Added canonical dataset validation, near-duplicate-grouped splits, response-only tokenization, and full/LoRA training workflows.
- Reviewed `data/expand_batch_2.py` statically without executing it; documented its count mismatch, four conflicting responses, and destructive overwrite behavior.
- Added local inference, FastAPI and Streamlit interfaces, and kept the existing 22-example benchmark and its results.
- Added a separate 110-question benchmark with 10 questions for each of the 11 topics, 40 independently checked calculation cases, five question types, and no exact or high-TF-IDF-similarity training prompts.
- Added a Decimal calculation engine with tests for all 20 operation types, invalid inputs, and edge cases.
- Added dated local-source retrieval, citations, missing/outdated-source signaling, and explicit separation of source facts, tool calculations, and model-generated explanations in the API and UI.
- Audited all six v2 JSON reports and their 110-row CSVs; outputs share a single benchmark hash, include the same unique 110 IDs, and preserve the original reports. Added six separate 110-row human review CSVs with blank fields for factual correctness, relevance, completeness, calculation correctness, grounding, and safety.
- Added a dimension-specific 0–5 [human evaluation guide](human-evaluation-guide.md) with examples and inter-rater guidance.
- Audited all eight curated excerpts (four unique official URLs/source IDs) and checked the four official pages on November 1, 2026. Found that the historical TF-IDF matcher returned unrelated passages. Added source-scope anchors; a separate current-retrieval probe matched 2/110 prompts, only partially supporting both. Historical model comparison reports are unchanged.
- Compared base GPT-2, full-v2, and LoRA-v2 alone, plus base GPT-2 with calculation, retrieval, and both, on the same benchmark fingerprint. See the [final evaluation report](../reports/evaluation/financial_benchmark_v2_final.md) and its per-arm outputs.
- All 40 numerical cases matched their 70 independently checked expected output values in the deterministic calculator arms. This does not indicate improved GPT-2 accuracy.
- Added and passed a Streamlit AppTest UI workflow and a FastAPI end-to-end TestClient flow using a fake model, verifying separate model text, calculator output, source evidence, and uncertainty.
- Final quality-audit verification: all 91 automated tests passed; the changed Python files also passed `compileall`. The application workflow tests use a fake model and do not verify real model answer quality.
- No new training run was started; model files and previous evaluation reports were preserved.

## Current evaluation limitations

- Model numeric-value coverage was 1/70 for base GPT-2, 5/70 for full-v2, and 1/70 for LoRA-v2. This automated presence check is not a factual-accuracy score.
- The historical retrieval corpus is small. Its prior 37/110 lexical matches included irrelevant excerpts; the stricter audited matcher returned only 2/110 partial matches. It has low recall and no complete coverage.
- All six new human-review CSVs are blank. Human rubric scoring and external review of jurisdiction- and date-dependent statements remain outstanding.
- Automated Streamlit workflow checks pass, but no broader visual/usability review has been performed.
- The earlier full-v2 manual review on the 22-question benchmark remains unchanged: 15 FAIL, 7 REVIEW, 0 PASS.

## Release gate

The model **fails the release gate**. Do not present it as a validated financial assistant or use it for consequential decisions. Human review, broader source coverage, and external verification of time-sensitive regulatory claims remain necessary. All generated explanations remain unverified; calculation outputs are limited to the supported functions and supplied assumptions.
