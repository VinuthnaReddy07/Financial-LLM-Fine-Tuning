from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from financial_llm.data.dataset import (  # noqa: E402
    dataset_sha256,
    find_exact_instruction_duplicates,
    load_examples,
    validate_examples,
)

SOURCE = PROJECT_ROOT / "data" / "raw" / "financial_dataset_expanded_305_raw.json"
OUTPUT = PROJECT_ROOT / "data" / "validated" / "financial_dataset_v1.json"
AUDIT_JSON = PROJECT_ROOT / "reports" / "dataset_quality" / "dataset_audit_v1.json"
AUDIT_MD = PROJECT_ROOT / "reports" / "dataset_quality" / "dataset_quality_v1.md"

REMOVALS = {
    36: "Same asset-allocation definition as record 43; retained the clearer canonical definition.",
    178: "Repeated the risk-return trade-off already covered in records 42 and 80.",
    243: "Repeated the gross/operating-profit calculation skill covered more completely in record 305.",
    257: "Repeated the retirement-inflation explanation in record 229.",
    269: "Repeated the AI error-logging and feedback topic in record 253.",
    303: "Repeated the weighted-average purchase-price calculation in record 241.",
    304: "Repeated the emergency-fund months-of-coverage calculation in record 242.",
}

REVIEW_NOTES: dict[int, dict[str, str]] = {
    10: {
        "issue": "Definition could imply that every bond pays periodic interest.",
        "action": "correct",
        "suggestion": "Clarify that cash flows and return structure depend on bond terms; some bonds do not pay periodic interest.",
    },
    21: {
        "issue": "APR fee inclusion varies by jurisdiction and credit product.",
        "action": "correct",
        "suggestion": "Describe APR as an annualized borrowing-cost measure and qualify fee treatment by applicable rules and product disclosures.",
    },
    36: {
        "issue": "Near-duplicate of asset allocation definition in record 43.",
        "action": "remove",
        "suggestion": "Retain record 43 as the canonical definition.",
    },
    43: {
        "issue": "Near-duplicate of portfolio allocation definition in record 36.",
        "action": "keep",
        "suggestion": "Retain one canonical asset-allocation definition.",
    },
    49: {
        "issue": "Related to record 111, which supplies the formula.",
        "action": "keep_distinct",
        "suggestion": "Use this as the plain-language definition and record 111 as the formula prompt.",
    },
    50: {
        "issue": "Grace-period meaning and interest/fee treatment vary by product and agreement.",
        "action": "correct",
        "suggestion": "Define the term generally and state that applicable fees and interest depend on the product agreement.",
    },
    51: {
        "issue": "Could be confused with the overdraft facility described in record 94.",
        "action": "correct",
        "suggestion": "Clarify that this describes an account balance falling below available funds when the bank permits it; record 94 describes the facility.",
    },
    64: {
        "issue": "The savings-rate denominator is not identified as gross or take-home income.",
        "action": "correct",
        "suggestion": "State that 20% uses the monthly income figure provided as the denominator.",
    },
    68: {
        "issue": "Bond cash-flow wording could imply that all bonds pay periodic interest.",
        "action": "correct",
        "suggestion": "Qualify payments and repayment by bond terms; some bonds do not pay periodic interest.",
    },
    77: {
        "issue": "Related to risk-return explanations in records 42, 80, and 178.",
        "action": "keep_distinct",
        "suggestion": "Keep the focus on uncertainty of actual versus expected return and risk of loss.",
    },
    80: {
        "issue": "Related to the risk-return trade-off in records 42, 77, and 178.",
        "action": "keep_distinct",
        "suggestion": "Keep as a direct misconception check: higher risk does not assure higher realized returns.",
    },
    83: {
        "issue": "Related to record 45, but adds the net-worth formula and examples.",
        "action": "keep_distinct",
        "suggestion": "Retain as the calculation/formula-focused version.",
    },
    85: {
        "issue": "Repeats the expense-ratio definition in records 39 and 159.",
        "action": "rewrite_instruction",
        "suggestion": "Focus on how operating expenses affect the investor's net return.",
    },
    94: {
        "issue": "Related to record 51 but addresses the approved facility, limit, and costs.",
        "action": "keep_distinct",
        "suggestion": "Keep this facility-focused explanation distinct from the overdraft event in record 51.",
    },
    111: {
        "issue": "Related to record 49, but supplies the calculation formula.",
        "action": "keep_distinct",
        "suggestion": "Retain as the formula-focused version.",
    },
    112: {
        "issue": "Answer uses gross monthly income, but the question only says monthly earnings.",
        "action": "correct_instruction",
        "suggestion": "Explicitly state that Rs. 60,000 is gross monthly income.",
    },
    171: {
        "issue": "Definition overlaps volatility definition in record 41.",
        "action": "rewrite",
        "suggestion": "Distinguish volatility as one measure of risk from risk more broadly.",
    },
    178: {
        "issue": "Repeated the risk-return trade-off already covered in records 42 and 80.",
        "action": "remove",
        "suggestion": "Retain distinct risk and misconception examples instead.",
    },
    225: {
        "issue": "Tax avoidance/evasion terminology and legal boundaries depend on jurisdiction and facts.",
        "action": "qualify",
        "suggestion": "Keep explicitly general, state that legal definitions vary, and direct readers to current official guidance.",
    },
    242: {
        "issue": "Same months-of-emergency-fund calculation as record 304.",
        "action": "keep",
        "suggestion": "Retain as the single example for this calculation skill.",
    },
    243: {
        "issue": "Near-duplicate of the operating-profit calculation in record 305.",
        "action": "remove",
        "suggestion": "Retain the richer two-step accounting calculation in record 305.",
    },
    257: {
        "issue": "Repeated the retirement-inflation explanation in record 229.",
        "action": "remove",
        "suggestion": "Retain the earlier retirement-inflation entry.",
    },
    269: {
        "issue": "Near-duplicate of the AI error-logging and feedback entry in record 253.",
        "action": "remove",
        "suggestion": "Retain record 253.",
    },
    303: {
        "issue": "Repeated the weighted-average purchase-price calculation in record 241.",
        "action": "remove",
        "suggestion": "Retain record 241.",
    },
    304: {
        "issue": "Repeated the emergency-fund months-of-coverage calculation in record 242.",
        "action": "remove",
        "suggestion": "Retain record 242.",
    },
    305: {
        "issue": "Related to record 243 but calculates both gross and operating profit.",
        "action": "keep_distinct",
        "suggestion": "Retain this two-step calculation as the more complete accounting example.",
    },
}

INSTRUCTION_UPDATES = {
    85: "How do a mutual fund's operating expenses affect an investor's returns?",
    112: "A person has gross monthly income of Rs. 60,000 and pays Rs. 15,000 toward loan EMIs. Calculate the debt-to-income ratio using these figures.",
    171: "Why is volatility only one measure of investment risk?",
}

RESPONSE_UPDATES = {
    10: (
        "A bond is a debt instrument issued by a company, government, or other entity. "
        "Its cash flows and repayment terms are set out in the bond's terms. Some bonds "
        "pay periodic interest, while others may not; repayment of principal is subject "
        "to the issuer's obligations and the bond terms."
    ),
    21: (
        "APR is an annualized measure of the cost of borrowing. Depending on the "
        "jurisdiction and credit product, its calculation may include interest and "
        "specified charges under applicable disclosure rules. Compare the product's "
        "official disclosures rather than assuming every fee is included."
    ),
    50: (
        "A grace period is a period allowed under a financial product's terms before "
        "a specified consequence applies. The meaning and treatment of interest or "
        "fees depend on the product and agreement. For a credit card, for example, "
        "eligible purchases may avoid interest if the required balance is paid by "
        "the due date, subject to the card terms."
    ),
    51: (
        "An overdraft occurs when payments take an account below its available balance "
        "and the bank permits the transactions. This describes the account situation; "
        "an overdraft facility is a separate approved borrowing arrangement whose "
        "limit, interest, fees, and repayment terms depend on the bank agreement."
    ),
    64: (
        "Savings rate = (monthly savings / the stated monthly income) × 100. "
        "(Rs. 8,000 / Rs. 40,000) × 100 = 20%. This uses the income figure in the "
        "question as the denominator; a rate based on gross versus take-home income "
        "would need that basis to be specified."
    ),
    68: (
        "A stock represents partial ownership in a company; its price can rise or fall, "
        "and dividends are not guaranteed. A bond is debt issued by a company, government, "
        "or other entity. A bond's payment and repayment terms depend on its documents; "
        "some bonds pay periodic interest and others do not. Both can involve loss and "
        "different risks."
    ),
    171: (
        "Volatility describes the size and frequency of price or return fluctuations "
        "over a measured period. It is one way to describe investment risk, but it does "
        "not capture every risk, such as default, liquidity, or concentration risk. "
        "Historical volatility also does not predict future returns."
    ),
    225: (
        "In broad educational usage, tax avoidance refers to arranging affairs within "
        "rules intended to reduce tax, while tax evasion refers to unlawful conduct "
        "such as concealing income or falsifying records. The legal boundary and "
        "terminology depend on the jurisdiction, current law, and facts. Check current "
        "official tax guidance or consult a qualified tax professional; do not treat "
        "this general distinction as legal advice."
    ),
}


def build(source: Path, output: Path, audit_json: Path, audit_md: Path) -> None:
    examples = load_examples(source)
    if len(examples) != 305:
        raise ValueError(f"Expected 305 source records; found {len(examples)}.")

    canonical: list[dict[str, str]] = []
    records: list[dict[str, Any]] = []
    for original_number, original in enumerate(examples, start=1):
        note = REVIEW_NOTES.get(original_number)
        if original_number in REMOVALS:
            records.append({
                "source_record": original_number,
                "classification": "REVIEW",
                "disposition": "remove",
                "instruction": original["instruction"],
                "issue": REMOVALS[original_number],
                "suggested_correction": note["suggestion"] if note else "",
                "canonical_record": None,
            })
            continue

        updated = dict(original)
        if original_number in INSTRUCTION_UPDATES:
            updated["instruction"] = INSTRUCTION_UPDATES[original_number]
        if original_number in RESPONSE_UPDATES:
            updated["response"] = RESPONSE_UPDATES[original_number]
        canonical.append(updated)
        records.append({
            "source_record": original_number,
            "classification": "REVIEW" if note else "PASS",
            "disposition": note["action"] if note else "keep",
            "instruction": original["instruction"],
            "issue": note["issue"] if note else "",
            "suggested_correction": note["suggestion"] if note else "",
            "canonical_record": len(canonical),
            "updated_instruction": updated["instruction"],
            "updated_response": updated["response"] if updated != original else None,
        })

    validate_examples(canonical)
    duplicate_instructions = find_exact_instruction_duplicates(canonical)
    if duplicate_instructions:
        raise ValueError(f"Exact duplicate canonical instructions: {duplicate_instructions}")

    output.parent.mkdir(parents=True, exist_ok=True)
    audit_json.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(canonical, file, ensure_ascii=False, indent=2)
        file.write("\n")

    report = {
        "source_file": str(source.relative_to(PROJECT_ROOT)),
        "source_sha256": dataset_sha256(source),
        "source_records": len(examples),
        "canonical_records": len(canonical),
        "removed_records": sorted(REMOVALS),
        "corrected_record_ids": sorted(set(INSTRUCTION_UPDATES) | set(RESPONSE_UPDATES)),
        "reviewed_records": len(REVIEW_NOTES),
        "pass_records": len(examples) - len(REVIEW_NOTES),
        "review_records": len(REVIEW_NOTES),
        "fail_records": 0,
        "external_verification_required": [
            {"record": 21, "topic": "APR disclosures", "reason": "Product- and jurisdiction-specific fee inclusion."},
            {"record": 95, "topic": "Indian payment systems", "reason": "Current operating details, limits, and charges can change."},
            {"record": 98, "topic": "Dormant accounts", "reason": "Applicable banking rules and account treatment vary by jurisdiction and bank."},
            {"record": 110, "topic": "Loan foreclosure", "reason": "Charges and restrictions depend on contract and current law."},
            {"record": 114, "topic": "Credit enquiries", "reason": "Scoring-system and bureau practices vary."},
            {"record": 117, "topic": "Credit enquiries", "reason": "Credit-score impact depends on scoring systems and reporting rules."},
            {"record": 118, "topic": "Credit enquiries", "reason": "Treatment depends on the applicable credit-reporting system."},
            {"record": 120, "topic": "Credit report disputes", "reason": "Dispute processes and deadlines vary by jurisdiction and bureau."},
            {"record": 123, "topic": "Credit-card grace periods", "reason": "Terms depend on the particular card agreement and jurisdiction."},
            {"record": 124, "topic": "Credit-card late payment", "reason": "Fees, interest, and reporting depend on agreement and applicable rules."},
            {"record": 149, "topic": "IPOs", "reason": "Offering and listing processes depend on current market regulations."},
            {"record": 161, "topic": "Mutual-fund disclosures", "reason": "Document names and required disclosures depend on the market and current regulation."},
            {"record": 217, "topic": "Insurance grievances", "reason": "Official complaint and appeal routes are jurisdiction-dependent."},
            {"record": 225, "topic": "Tax avoidance and evasion", "reason": "Legal definitions and boundaries depend on current local law and facts."},
            {"record": 226, "topic": "Tax guidance", "reason": "Any actual tax answer requires the correct jurisdiction and tax year."},
            {"record": 227, "topic": "Tax filing", "reason": "Filing documents and requirements depend on jurisdiction, income, and year."},
            {"record": 267, "topic": "Privacy/security", "reason": "Legal duties depend on applicable privacy and financial regulations."},
            {"record": 273, "topic": "UPI incident response", "reason": "Official reporting channels and deadlines are time-sensitive."},
            {"record": 286, "topic": "Indian mutual-fund plans", "reason": "Plan rules and expense disclosures require current official scheme documents."},
            {"record": 287, "topic": "Mutual-fund exit loads", "reason": "Current terms are scheme-specific."},
            {"record": 296, "topic": "Indian tax years", "reason": "Tax year terminology and deadlines must be verified against current official guidance."},
            {"record": 297, "topic": "Tax deductions", "reason": "Eligibility depends on tax regime, year, and current rules."},
            {"record": 301, "topic": "Indirect tax calculation", "reason": "The prompt supplies a hypothetical rate; it is not asserted as a current tax rate."},
        ],
        "limitations": [
            "Content review is educational and static; no item is a substitute for professional legal, tax, accounting, or financial review.",
            "Current regulatory claims have not been independently source-verified in this build.",
            "Topic categories are assigned by the separate audit report and may overlap.",
        ],
        "records": records,
    }
    with audit_json.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
        file.write("\n")

    lines = [
        "# Dataset quality review — version 1",
        "",
        f"- Source: `{report['source_file']}`",
        f"- Source SHA-256: `{report['source_sha256']}`",
        f"- Source records: {len(examples)}",
        f"- Canonical records: {len(canonical)}",
        f"- Reviewed: {len(REVIEW_NOTES)} (PASS {report['pass_records']}, REVIEW {report['review_records']}, FAIL 0)",
        f"- Removed as redundant: {len(REMOVALS)}",
        f"- Records with response or instruction edits: {len(set(INSTRUCTION_UPDATES) | set(RESPONSE_UPDATES))}",
        "",
        "## Policy",
        "",
        "The original source is preserved. The canonical file contains only `instruction` and `response` fields. "
        "Redundant prompts were removed only where the underlying task was substantially repeated; related "
        "definition, formula, and scenario questions were retained when they teach distinguishable skills. "
        "No current tax rate, regulatory threshold, product term, or legal rule was treated as externally verified.",
        "",
        "## Dispositions",
        "",
        "| Source record | Decision | Summary |",
        "|---:|---|---|",
    ]
    for item in records:
        if item["classification"] == "REVIEW":
            summary = item["issue"].replace("|", "\\|")
            lines.append(f"| {item['source_record']} | {item['disposition']} | {summary} |")
    lines += [
        "",
        "## External verification required before publishing time-sensitive guidance",
        "",
    ]
    for item in report["external_verification_required"]:
        lines.append(f"- Record {item['record']} — {item['topic']}: {item['reason']}")
    lines += [
        "",
        "## Remaining limitations",
        "",
        *[f"- {limitation}" for limitation in report["limitations"]],
        "",
    ]
    with audit_md.open("w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(lines))
    print(f"Canonical dataset: {output} ({len(canonical)} records)")
    print(f"Audit report: {audit_md}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build reviewed data into a new canonical file.")
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--audit-json", type=Path, default=AUDIT_JSON)
    parser.add_argument("--audit-markdown", type=Path, default=AUDIT_MD)
    args = parser.parse_args()
    for path in (args.output, args.audit_json, args.audit_markdown):
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    build(args.source, args.output, args.audit_json, args.audit_markdown)


if __name__ == "__main__":
    main()
