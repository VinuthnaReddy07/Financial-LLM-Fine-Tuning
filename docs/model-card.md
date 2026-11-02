# Model card

## Intended use

Local experimentation and educational explanations about general financial concepts. The model is not suitable for personalized financial, tax, insurance, or legal advice; execution decisions; or determining current rates, eligibility, product terms, or legal obligations.

## Model and training

The configured base is `openai-community/gpt2`. The shared runner supports full fine-tuning and PEFT LoRA over the reviewed tokenized data, with fixed seed, response-only training labels, and per-epoch validation metrics. New runs must use unique output paths and load all model/tokenizer inputs from local files.

Existing directories under `models/` are legacy artifacts. They were created before the reviewed v1 pipeline and have different historical settings. The v2 benchmark reports measure existing base, full-v2, and LoRA-v2 artifacts; no training was started during the final quality audit. Do not infer performance from filenames or training loss alone.

## Risks and limitations

GPT-2 can produce fabricated, incomplete, repetitive, stale, or overconfident financial statements. It may fail arithmetic, omit jurisdiction, or echo unsafe premises. The fixed benchmark and manual review sheet support evaluation but do not prove safety or professional accuracy. Do not use generated answers as a sole basis for financial action.

The measured full-v2 run produced 22 benchmark outputs. Manual review classified 15 FAIL, 7 REVIEW, and 0 PASS; both exact calculation checks failed. The base and both LoRA runs each failed both exact calculation checks. These outputs do not meet the release gate; the UI and API require explicit opt-in and visibly identify the model as experimental. See [the full manual review](../reports/evaluation/full-v2_manual_review.md).

## Application-level tools and expanded evaluation

The application can optionally call a deterministic Decimal-based calculator and retrieve excerpts from a small dated, curated local corpus. Responses preserve three provenance categories: retrieved facts/citations, calculation outputs/assumptions, and the model-generated explanation. Missing or overdue sources are reported as uncertainty. These tools change the application pipeline, not the GPT-2 weights or its standalone accuracy.

The 110-question v2 benchmark is kept outside training data and includes 40 calculation cases. Model-alone, retrieval, calculator, and combined-tool results are reported separately from human rubric scores. The calculation engine's numerical matches do not establish factual accuracy or financial suitability. See the [v2 evaluation report](../reports/evaluation/financial_benchmark_v2_final.md); generated outputs still require independent human review.

On v2, expected numeric values appeared in 1/70 model-generated values for base GPT-2, 5/70 for full-v2, and 1/70 for LoRA-v2. This is only an automated presence metric, not a correctness score. The calculator arms matched 70/70 expected structured values across the 40 calculation cases; model explanations in those arms did not reproduce the expected values. The retrieval arms found lexical matches for 37/110 prompts and surfaced no source for 73. The v2 human-review sheets remain unscored.

## Data and license

The fine-tuning derivative is described in the [data card](data-card.md). Verify the base model's license and any third-party data permissions before redistribution or deployment. This card makes no claim that those rights have been cleared.
