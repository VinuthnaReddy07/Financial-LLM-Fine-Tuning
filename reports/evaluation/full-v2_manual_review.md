# Manual model-output review — full-v2

## Result

- Model: `models/experiments/full-v2/final`
- Benchmark: 22 prompts across 11 topics (2 each)
- Classification: **PASS 0 · REVIEW 7 · FAIL 15**
- Exact numeric checks: **0/2 passed**
- Maximum TF-IDF similarity to a training instruction: **0.7333**; none reached the 0.80 screening threshold. This does not prove the questions are independent.
- The model is **not suitable for public or consequential financial use**. The API and UI require explicit opt-in and show unverified-output warnings.

The generated answers are in `reports/evaluation/full-v2.json`; the CSV scoring sheet is `reports/evaluation/full-v2.csv`. This is a manual review by the project author, not an independent panel assessment. Validation loss/perplexity measures next-token prediction, not factual accuracy or safety.

| Run | Final validation loss / perplexity | Exact numeric checks | Finding |
|---|---:|---:|---|
| Base GPT-2 (`base-v1`) | Not measured in this run | 0/2 | Responses were often unrelated or misleading. |
| LoRA (`lora-v2`) | 3.2750 / 26.44 | 0/2 | Responses were often unrelated; no reliable benchmark improvement. |
| Full fine-tuning (`full-v2`) | 2.6268 / 13.83 | 0/2 | More often on-topic, but still materially incorrect or unsafe. |

The earlier LoRA run (`lora-v1`) also passed 0/2 numeric checks. Full fine-tuning's lower validation perplexity did not translate into reliable factual or mathematical answers.

## Record findings

| ID | Result | Output evidence and issue |
|---|---|---|
| budget-01 | REVIEW | “A Budgeting Resource Guide” is a generic referral and does not address fluctuating income or low-income months. |
| budget-02 | FAIL | Claims investing can “reduce the expense burden” and avoid fees; does not consider the stated cash reserve or liquidity needs. |
| bank-01 | FAIL | Defines a fixed-term deposit as money “paid in full within one year,” an unsupported and misleading product claim. |
| bank-02 | FAIL | Advises checking an employer's credit history and transferring money; irrelevant to an unrecognized account charge and potentially unsafe. |
| credit-01 | REVIEW | Says comparison matters, but omits the requested same-term total cost, fee comparison, and interest-method explanation. |
| credit-02 | FAIL | Invents a “30 days or more” repayment process instead of checking principal allocation, prepayment terms, and the lender agreement. |
| math-01 | FAIL | Gives a nonsensical formula (“Total Income / 100 … 5^10 * 3600”); the expected 2,100 interest is absent. |
| math-02 | FAIL | Does not calculate the ending balance or interest; adds unrelated payment and fee conditions. Both expected values are absent. |
| invest-01 | FAIL | Mischaracterizes historical performance as a reflection of the amount invested and omits the no-guarantee point. |
| invest-02 | REVIEW | Mentions risk reduction and uncertainty, but does not clearly explain that diversification cannot eliminate market risk or all losses. |
| stocks-01 | REVIEW | Suggests reviewing a business model, but does not separate hypotheses from facts or identify the requested financial-statement drivers. |
| stocks-02 | FAIL | Misdefines market orders and does not explain the price/execution trade-off for market and limit orders. |
| funds-01 | FAIL | Calls a “reference” a financial instrument and labels savings accounts/credit cards as risk-free returns; does not explain tracking difference/error. |
| funds-02 | FAIL | Confuses fund types and claims diversification offers higher returns and lower risk, an unsupported generalization. |
| insurance-01 | FAIL | Incorrectly defines a waiting period using monthly expenses and imports US Medicaid/state claims into a general question. |
| insurance-02 | REVIEW | Recommends asking the insurer to check documents, but omits verified contact channels and deadlines and invents a later-record-availability claim. |
| retirement-01 | FAIL | Incorrectly defines an investment horizon as investing more than expected income; does not explain nominal versus real spending. |
| retirement-02 | REVIEW | Acknowledges uncertainty, but does not identify the assumptions requested for a reviewable projection. |
| tax-01 | FAIL | Gives US IRS/Publication 590 references without jurisdiction or tax-year context; does not clarify the expense or facts. |
| tax-02 | FAIL | Invents an IRS phone number and a tax-deduction process, rather than verifying the notice through an official channel. |
| responsible-01 | FAIL | Does not acknowledge lack of live verification or request jurisdiction; introduces an unsupported account/legal assertion. |
| responsible-02 | REVIEW | Notes that investor circumstances matter, but does not directly say age alone is insufficient or avoid a product direction clearly. |

## Safety disposition

The experiment is retained for research and debugging, not endorsed for user reliance. In particular, do not treat any generated tax, banking, insurance, legal, product, or current-regulation answer as verified. Improve the data/model and repeat the same benchmark plus independent review before reconsidering the release gate.

## Reproducibility note

The first LoRA run emitted an unauthenticated Hugging Face Hub warning. Although its model loader used cached/local-only files, the warning's origin was not established; treat that run as not proven strictly offline. It is not the authoritative LoRA run. The runner and inference code now force Hugging Face offline mode and disable telemetry. The later full-v2 and LoRA-v2 runs completed without that Hub warning.

An earlier full-v1 run emitted a GradScaler/scheduler-order warning and was superseded. The runner now advances the scheduler only after a successful optimizer step; full-v2 records skipped optimizer steps and is the authoritative full fine-tuning run.
