# Dataset quality review — version 1

- Source: `data\raw\financial_dataset_expanded_305_raw.json`
- Source SHA-256: `4c11606da500ca60cb492753ebe20bf448e86ed2dc780967c31a91697d73e12c`
- Source records: 305
- Canonical records: 298
- Reviewed: 26 (PASS 279, REVIEW 26, FAIL 0)
- Removed as redundant: 7
- Records with response or instruction edits: 10

## Policy

The original source is preserved. The canonical file contains only `instruction` and `response` fields. Redundant prompts were removed only where the underlying task was substantially repeated; related definition, formula, and scenario questions were retained when they teach distinguishable skills. No current tax rate, regulatory threshold, product term, or legal rule was treated as externally verified.

## Dispositions

| Source record | Decision | Summary |
|---:|---|---|
| 10 | correct | Definition could imply that every bond pays periodic interest. |
| 21 | correct | APR fee inclusion varies by jurisdiction and credit product. |
| 36 | remove | Same asset-allocation definition as record 43; retained the clearer canonical definition. |
| 43 | keep | Near-duplicate of portfolio allocation definition in record 36. |
| 49 | keep_distinct | Related to record 111, which supplies the formula. |
| 50 | correct | Grace-period meaning and interest/fee treatment vary by product and agreement. |
| 51 | correct | Could be confused with the overdraft facility described in record 94. |
| 64 | correct | The savings-rate denominator is not identified as gross or take-home income. |
| 68 | correct | Bond cash-flow wording could imply that all bonds pay periodic interest. |
| 77 | keep_distinct | Related to risk-return explanations in records 42, 80, and 178. |
| 80 | keep_distinct | Related to the risk-return trade-off in records 42, 77, and 178. |
| 83 | keep_distinct | Related to record 45, but adds the net-worth formula and examples. |
| 85 | rewrite_instruction | Repeats the expense-ratio definition in records 39 and 159. |
| 94 | keep_distinct | Related to record 51 but addresses the approved facility, limit, and costs. |
| 111 | keep_distinct | Related to record 49, but supplies the calculation formula. |
| 112 | correct_instruction | Answer uses gross monthly income, but the question only says monthly earnings. |
| 171 | rewrite | Definition overlaps volatility definition in record 41. |
| 178 | remove | Repeated the risk-return trade-off already covered in records 42 and 80. |
| 225 | qualify | Tax avoidance/evasion terminology and legal boundaries depend on jurisdiction and facts. |
| 242 | keep | Same months-of-emergency-fund calculation as record 304. |
| 243 | remove | Repeated the gross/operating-profit calculation skill covered more completely in record 305. |
| 257 | remove | Repeated the retirement-inflation explanation in record 229. |
| 269 | remove | Repeated the AI error-logging and feedback topic in record 253. |
| 303 | remove | Repeated the weighted-average purchase-price calculation in record 241. |
| 304 | remove | Repeated the emergency-fund months-of-coverage calculation in record 242. |
| 305 | keep_distinct | Related to record 243 but calculates both gross and operating profit. |

## External verification required before publishing time-sensitive guidance

- Record 21 — APR disclosures: Product- and jurisdiction-specific fee inclusion.
- Record 95 — Indian payment systems: Current operating details, limits, and charges can change.
- Record 98 — Dormant accounts: Applicable banking rules and account treatment vary by jurisdiction and bank.
- Record 110 — Loan foreclosure: Charges and restrictions depend on contract and current law.
- Record 114 — Credit enquiries: Scoring-system and bureau practices vary.
- Record 117 — Credit enquiries: Credit-score impact depends on scoring systems and reporting rules.
- Record 118 — Credit enquiries: Treatment depends on the applicable credit-reporting system.
- Record 120 — Credit report disputes: Dispute processes and deadlines vary by jurisdiction and bureau.
- Record 123 — Credit-card grace periods: Terms depend on the particular card agreement and jurisdiction.
- Record 124 — Credit-card late payment: Fees, interest, and reporting depend on agreement and applicable rules.
- Record 149 — IPOs: Offering and listing processes depend on current market regulations.
- Record 161 — Mutual-fund disclosures: Document names and required disclosures depend on the market and current regulation.
- Record 217 — Insurance grievances: Official complaint and appeal routes are jurisdiction-dependent.
- Record 225 — Tax avoidance and evasion: Legal definitions and boundaries depend on current local law and facts.
- Record 226 — Tax guidance: Any actual tax answer requires the correct jurisdiction and tax year.
- Record 227 — Tax filing: Filing documents and requirements depend on jurisdiction, income, and year.
- Record 267 — Privacy/security: Legal duties depend on applicable privacy and financial regulations.
- Record 273 — UPI incident response: Official reporting channels and deadlines are time-sensitive.
- Record 286 — Indian mutual-fund plans: Plan rules and expense disclosures require current official scheme documents.
- Record 287 — Mutual-fund exit loads: Current terms are scheme-specific.
- Record 296 — Indian tax years: Tax year terminology and deadlines must be verified against current official guidance.
- Record 297 — Tax deductions: Eligibility depends on tax regime, year, and current rules.
- Record 301 — Indirect tax calculation: The prompt supplies a hypothetical rate; it is not asserted as a current tax rate.

## Remaining limitations

- Content review is educational and static; no item is a substitute for professional legal, tax, accounting, or financial review.
- Current regulatory claims have not been independently source-verified in this build.
- Topic categories are assigned by the separate audit report and may overlap.
