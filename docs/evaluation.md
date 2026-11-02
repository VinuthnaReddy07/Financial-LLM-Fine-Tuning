# Evaluation protocol

`data/evaluation/manual_benchmark_v1.json` is a preserved 22-prompt benchmark. The independent `data/evaluation/financial_benchmark_v2.json` contains 110 authored prompts: 10 per each of the project's 11 topics, with conceptual, factual, multi-step, uncertainty-handling, and 40 numerical calculation cases. It is not part of any training split. Its builder is `src/financial_llm/evaluation/build_benchmark_v2.py`; the runner reports exact training-prompt matches and TF-IDF near-duplicate screening for human inspection.

The v2 comparison runner uses the same prompt file and generation settings for the base model, full-v2, LoRA-v2, and each tool-assisted arm. The tool arms keep model-generated explanations separate from structured calculations and retrieved snippets. Calculation checks compare the deterministic tool output against the independently stated benchmark values; model number coverage only measures whether expected numerals appeared and is not a correctness score. Retrieval counts likewise do not indicate whether a generated response is correct.

## Human review

The original six comparison CSVs are preserved; their scoring columns do not cover all dimensions requested for this audit. Six separate sheets with all required dimensions are created at `reports/evaluation/benchmark_v2/human_review_v2/`. Run `python -m financial_llm.evaluation.build_human_review_sheets` with `PYTHONPATH=src` to regenerate into a new output directory; existing sheets are never overwritten.

Every new sheet has a blank 0–5 field for factual correctness, relevance, completeness, calculation correctness, grounding, and safety, plus the relevant structured calculator result and retrieved source evidence. Score each dimension independently. Use `N/A` for calculation correctness on conceptual/non-numeric questions. Keep original scores if adjudicating disagreements. The [human evaluation guide](human-evaluation-guide.md) contains dimension-specific anchors, examples, and reviewer reconciliation instructions.

Review each response for:

1. Factual correctness and whether uncertainty is acknowledged.
2. Completeness against the listed expected points.
3. Clarity and directness.
4. Safety: no invented current rules, guaranteed returns, or unjustified personalized recommendations.
5. Exact calculation and units where the benchmark provides expected numbers; score arithmetic separately from model wording.
6. Similarity to training prompts; investigate high-similarity items as possible prompt leakage.

Resolve incorrect or unsafe answers before any public use. Model numeric coverage checks whether expected numbers appear and is not a full calculation or factual score. The calculator arm's output check compares its structured values with the benchmark's independently specified values. TF-IDF similarity is a screening signal, not proof of semantic independence.

For model comparisons, use the same benchmark, tokenized train/validation/test files, generation settings, and human rubric. Keep each run's output unique. Report actual results and hardware; do not claim improved accuracy without a reproducible comparative evaluation.

## Current status

Automated v2 output is not human evaluation. The new human review sheets have not been scored. The historical retrieval comparison reported matches for 37/110 questions; audit found unrelated matches, so the current corpus adds source-scope anchors. Re-running the current retriever over the benchmark returned 2/110 partial matches and 108 missing-source results. The historical six reports are preserved and reflect the earlier retrieval matcher; do not conflate their retrieval counts with the current matcher. Report model-alone, tool-assisted, retrieval, and human rubric results separately; external tools do not demonstrate that GPT-2 itself became more accurate.
