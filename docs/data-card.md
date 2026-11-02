# Data card

## Dataset lineage

- Immutable audit input: `data/raw/financial_dataset_expanded_305_raw.json`
- Input SHA-256: `4c11606da500ca60cb492753ebe20bf448e86ed2dc780967c31a91697d73e12c`
- Reviewed derivative: `data/validated/financial_dataset_v1.json`
- Reviewed derivative records: 298
- Train/validation/test: 238/30/30, with near-duplicate prompt groups kept within one split
- Tokenized maximum length: 160; response-only labels; EOS retained

The original 305 records and pre-existing datasets/checkpoints were preserved. Seven redundant source records were excluded from the derivative; ten records were clarified or corrected. The static audit classified source records as 279 PASS, 26 REVIEW, and 0 FAIL. See [the full audit](../reports/dataset_quality/dataset_quality_v1.md) for individual dispositions and limitations.

## Intended use and limitations

Use for local experiments in general financial education and language-model evaluation. The data are not an authoritative source of current product terms, tax rules, law, market data, banking limits, or regulatory requirements. Jurisdiction-dependent statements require current official verification. The dataset does not carry category labels; the separate manual benchmark has 11 broad topics with two prompts each, which is not a measured category distribution of the training data.

The review is static, not a substitute for expert legal, tax, accounting, insurance, or financial review. Corrections in the derivative do not update original source files.
