# Financial benchmark v2: results and limitations

## Scope and reproducibility

The independent benchmark contains 110 prompts: 10 in each of the project's 11 financial topics, including 40 numerical calculation cases. It covers conceptual, factual, multi-step, uncertainty-handling, and calculation questions. It is stored separately from the training split.

All six runs used the same benchmark SHA-256 `8e89f8f1effc7b75fe782dd35ff6cbf0ace8a65275fd22ea5de5eab853bb3a9b`, the same training split, and deterministic generation (`do_sample=false`, 100 maximum new tokens, repetition penalty 1.1, no-repeat n-gram size 3). The benchmark had no exact training-prompt matches, no prompts with TF-IDF similarity at or above 0.8, and a maximum similarity of 0.6538. Similarity screening cannot rule out semantic overlap.

The `model values present` column counts expected numeric values found in the generated explanation. It is only an automated coverage signal; it does not prove that the calculation, explanation, or answer is correct. Calculator values are evaluated separately by exact comparison with benchmark values independently checked using reference formulas. A blank human-review CSV is provided for every run. No human scores have been entered, so this report makes no overall factual-accuracy or safety claim.

## Results

| Arm | Generated explanation: expected values present | Deterministic calculator: exact values | Retrieval |
|---|---:|---:|---|
| A. Base GPT-2 alone | 1 / 70 | Not used | Not used |
| B. Full-v2 alone | 5 / 70 | Not used | Not used |
| C. Base GPT-2 + calculator | 0 / 70 | 70 / 70 | Not used |
| D. Base GPT-2 + retrieval | 1 / 70 | Not used | 37 found, 73 missing, 0 outdated / 110 |
| E. Base GPT-2 + retrieval + calculator | 0 / 70 | 70 / 70 | 37 found, 73 missing, 0 outdated / 110 |
| Additional: LoRA-v2 alone | 1 / 70 | Not used | Not used |

The calculator returned all expected output values for all 40 benchmark calculation cases. In the calculator arms, the model-generated explanation itself did not reproduce the expected values; the structured calculation remains a separate application output. This demonstrates tool arithmetic on these test inputs, not improved GPT-2 accuracy.

Retrieval used the dated local corpus with a conservative TF-IDF minimum score of 0.15. It returned 51 cited excerpts across 37 query records and no source for 73 records. The 37 matches do not establish that a source fully answers the question. The corpus is small and only covers limited RBI payment-system, SEBI investor-awareness, Income Tax Department portal, and IRDAI policyholder material. The live comparison had no overdue results; automated tests separately verified that past-review-date sources are marked outdated. Retrieval is not live browsing.

### Retrieval matches by benchmark topic

| Topic | Queries with a lexical match |
|---|---:|
| Banking and financial products | 4 / 10 |
| Interest and financial mathematics | 0 / 10 |
| Loans and credit management | 3 / 10 |
| Budgeting and personal finance | 7 / 10 |
| Stocks and market fundamentals | 4 / 10 |
| Mutual funds and portfolio management | 1 / 10 |
| Investment risk and analysis | 3 / 10 |
| Accounting and financial statements | 2 / 10 |
| Insurance and taxation | 10 / 10 |
| Retirement and financial planning | 2 / 10 |
| Financial AI safety | 1 / 10 |

Each topic still has 10 benchmark questions. These retrieval counts describe lexical matches only, not topic accuracy or answer coverage.

## Interpretation and release status

The small automated number-presence totals for model-only answers do not support a claim that base, full fine-tuning, or LoRA is accurate. The tool-assisted arms demonstrate exact calculation output for the 40 fixed calculation cases, but do not validate generated prose, assumptions outside those cases, tax treatment, policy interpretation, or financial suitability. The retrieval component is constrained by its short source corpus and lexical search; cited material must be checked for scope and currency.

The earlier 22-question manual review of full-v2 (15 FAIL, 7 REVIEW, 0 PASS) remains unchanged. The new review sheets are intentionally blank and require a reviewer to score factual accuracy, completeness, clarity, and safety using the anchors in [evaluation guidance](../../docs/evaluation.md). Until that review and source verification are complete, the model remains experimental and fails the release gate.

## Files

Each JSON report contains the same benchmark fingerprint, all 110 prompts and model outputs, per-topic metrics, source citations where retrieved, and calculation provenance. The corresponding CSV is the blank human-review sheet.

- [Base GPT-2 alone](./benchmark_v2/v2-base-alone.json)
- [Base GPT-2 review sheet](./benchmark_v2/v2-base-alone.csv)
- [Full-v2 alone](./benchmark_v2/v2-full-v2-alone.json)
- [Full-v2 review sheet](./benchmark_v2/v2-full-v2-alone.csv)
- [Base GPT-2 + calculator](./benchmark_v2/v2-base-calculator.json)
- [Base GPT-2 + calculator review sheet](./benchmark_v2/v2-base-calculator.csv)
- [Base GPT-2 + retrieval](./benchmark_v2/v2-base-retrieval.json)
- [Base GPT-2 + retrieval review sheet](./benchmark_v2/v2-base-retrieval.csv)
- [Base GPT-2 + retrieval + calculator](./benchmark_v2/v2-base-retrieval-calculator.json)
- [Combined-tools review sheet](./benchmark_v2/v2-base-retrieval-calculator.csv)
- [LoRA-v2 alone](./benchmark_v2/v2-lora-v2-alone.json)
- [LoRA-v2 review sheet](./benchmark_v2/v2-lora-v2-alone.csv)
