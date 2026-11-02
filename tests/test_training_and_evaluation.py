from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import torch
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from app.api import create_app  # noqa: E402
from financial_llm.calculations import CALCULATORS  # noqa: E402
from financial_llm.data.dataset import load_examples  # noqa: E402
from financial_llm.evaluation.run_benchmark import (  # noqa: E402
    _numeric_check,
    _similarity_scores,
    _tool_check,
    load_benchmark,
    write_human_review_sheet,
)
from financial_llm.retrieval import FinancialRetriever  # noqa: E402
from financial_llm.service import FinancialApplication  # noqa: E402
from financial_llm.training.train import (  # noqa: E402
    TokenizedDataset,
    collate_batch,
    optimizer_step_succeeded,
)


def test_collate_batch_pads_inputs_masks_and_ignores_label_padding() -> None:
    examples = [
        {
            "input_ids": torch.tensor([1, 2, 3]),
            "attention_mask": torch.tensor([1, 1, 1]),
            "labels": torch.tensor([-100, 2, 3]),
        },
        {
            "input_ids": torch.tensor([4]),
            "attention_mask": torch.tensor([1]),
            "labels": torch.tensor([4]),
        },
    ]

    batch = collate_batch(examples, pad_token_id=99)

    assert batch["input_ids"].tolist() == [[1, 2, 3], [4, 99, 99]]
    assert batch["attention_mask"].tolist() == [[1, 1, 1], [1, 0, 0]]
    assert batch["labels"].tolist() == [[-100, 2, 3], [4, -100, -100]]


def test_tokenized_dataset_rejects_mismatched_labels(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(
        json.dumps(
            [{"input_ids": [1, 2], "attention_mask": [1, 1], "labels": [-100]}]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid labels"):
        TokenizedDataset(path)


def test_tokenized_dataset_rejects_records_without_supervised_tokens(
    tmp_path: Path,
) -> None:
    path = tmp_path / "bad.json"
    path.write_text(
        json.dumps(
            [
                {
                    "input_ids": [1, 2],
                    "attention_mask": [1, 1],
                    "labels": [-100, -100],
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="no supervised response tokens"):
        TokenizedDataset(path)


def test_numeric_check_requires_all_expected_values() -> None:
    assert _numeric_check("Interest is 2,100.", [2100]) is True
    assert _numeric_check("Balance is 22,472.", [22472, 2472]) is False
    assert _numeric_check("No calculation needed.", []) is None


def test_tool_calculation_check_requires_exact_expected_values() -> None:
    exact = {"values": {"rate_percent": "5.89%"}}
    rounded_differently = {"values": {"rate_percent": "5.90%"}}
    assert _tool_check(exact, {"rate_percent": "5.89%"}) == {
        "expected_values": 1,
        "matched_values": 1,
        "all_values_correct": True,
    }
    assert _tool_check(rounded_differently, {"rate_percent": "5.89%"}) == {
        "expected_values": 1,
        "matched_values": 0,
        "all_values_correct": False,
    }


def test_optimizer_step_is_detected_from_gradient_scaler_scale() -> None:
    assert optimizer_step_succeeded(8.0, 8.0)
    assert optimizer_step_succeeded(8.0, 16.0)
    assert not optimizer_step_succeeded(8.0, 4.0)


def test_manual_benchmark_has_22_unique_records_and_11_topics() -> None:
    benchmark = load_benchmark(ROOT / "data" / "evaluation" / "manual_benchmark_v1.json")
    assert len(benchmark) == 22
    assert len({item["id"] for item in benchmark}) == len(benchmark)
    assert len({item["topic"] for item in benchmark}) == 11


def test_v2_benchmark_has_110_independent_prompts_and_40_calculations() -> None:
    benchmark = load_benchmark(ROOT / "data" / "evaluation" / "financial_benchmark_v2.json")
    training = load_examples(ROOT / "data" / "processed" / "train.json")
    normalized_training = {
        " ".join(item["instruction"].casefold().split()) for item in training
    }
    prompts = [item["instruction"] for item in benchmark]
    similarities = _similarity_scores(
        prompts, [item["instruction"] for item in training]
    )
    assert len(benchmark) == 110
    assert len({item["id"] for item in benchmark}) == 110
    assert len({item["instruction"] for item in benchmark}) == 110
    assert len({item["topic"] for item in benchmark}) == 11
    assert sum(item["calculation_case"] is not None for item in benchmark) == 40
    assert not any(
        " ".join(prompt.casefold().split()) in normalized_training
        for prompt in prompts
    )
    assert max(item["max_tfidf_similarity"] for item in similarities) < 0.8
    assert {
        item["question_type"] for item in benchmark
    } == {"conceptual", "factual", "multi_step", "uncertainty", "calculation"}


def test_v2_benchmark_expected_calculations_match_independent_formulas() -> None:
    import math

    benchmark = load_benchmark(ROOT / "data" / "evaluation" / "financial_benchmark_v2.json")
    cases = [item["calculation_case"] for item in benchmark if item["calculation_case"]]

    def reference(case: dict[str, object]) -> dict[str, float]:
        kind = case["type"]
        values = case["inputs"]
        assert isinstance(values, dict)
        if kind == "simple_interest":
            interest = values["principal"] * values["annual_rate_percent"] / 100 * values["years"]
            return {"interest": interest, "ending_balance": values["principal"] + interest}
        if kind == "compound_interest":
            balance = values["principal"] * (
                1 + values["annual_rate_percent"] / 100 / values["periods_per_year"]
            ) ** (values["periods_per_year"] * values["years"])
            return {"interest": balance - values["principal"], "ending_balance": balance}
        if kind == "percentage_change":
            change = values["ending_value"] - values["starting_value"]
            return {"absolute_change": change, "change_percent": change / values["starting_value"] * 100}
        if kind == "discount_price":
            discount = values["list_price"] * values["discount_percent"] / 100
            return {"discount_amount": discount, "final_price": values["list_price"] - discount}
        if kind == "debt_to_income":
            return {"ratio_percent": values["monthly_debt_payments"] / values["gross_monthly_income"] * 100}
        if kind == "loan_payment":
            principal = values["principal"]
            count = values["number_of_monthly_payments"]
            rate = values["annual_rate_percent"] / 100 / 12
            payment = principal / count if rate == 0 else principal * rate * (1 + rate) ** count / ((1 + rate) ** count - 1)
            total = payment * count
            return {"monthly_payment": payment, "total_payments": total, "total_interest": total - principal}
        if kind == "cagr":
            return {"annualized_return_percent": ((values["ending_value"] / values["starting_value"]) ** (1 / values["years"]) - 1) * 100}
        if kind == "real_return":
            nominal, inflation = values["nominal_return_percent"], values["inflation_percent"]
            return {"real_return_percent": ((1 + nominal / 100) / (1 + inflation / 100) - 1) * 100, "approximate_real_return_percent": nominal - inflation}
        if kind == "expense_ratio_cost":
            return {"annualized_cost_estimate": values["investment_amount"] * values["expense_ratio_percent"] / 100}
        if kind == "emergency_fund_months":
            return {"months_covered": values["emergency_savings"] / values["monthly_essential_expenses"]}
        if kind == "weighted_average_cost":
            quantity = values["first_quantity"] + values["second_quantity"]
            cost = values["first_quantity"] * values["first_price"] + values["second_quantity"] * values["second_price"]
            return {"total_quantity": quantity, "total_cost": cost, "average_cost_per_unit": cost / quantity}
        if kind == "hypothetical_tax":
            tax = values["taxable_amount"] * values["hypothetical_rate_percent"] / 100
            return {"illustrative_tax": tax, "amount_after_illustrative_tax": values["taxable_amount"] - tax}
        if kind == "budget_allocation":
            return {
                "needs_amount": values["monthly_income"] * values["needs_percent"] / 100,
                "wants_amount": values["monthly_income"] * values["wants_percent"] / 100,
                "savings_amount": values["monthly_income"] * values["savings_percent"] / 100,
            }
        if kind == "insurance_cost_share":
            deductible = min(values["covered_bill"], values["deductible"])
            member_share = deductible + (values["covered_bill"] - deductible) * values["copay_percent"] / 100
            return {"member_share": member_share, "illustrative_insurer_share": values["covered_bill"] - member_share}
        if kind == "net_cash_flow":
            return {"net_cash_flow": values["cash_inflows"] - values["cash_outflows"]}
        if kind == "profit_margin":
            return {"profit_margin_percent": values["profit"] / values["revenue"] * 100}
        if kind == "current_ratio":
            return {"current_ratio": values["current_assets"] / values["current_liabilities"]}
        if kind == "portfolio_weighted_return":
            return {"weighted_return_percent": (values["first_weight_percent"] * values["first_return_percent"] + values["second_weight_percent"] * values["second_return_percent"]) / 100}
        if kind == "savings_rate":
            return {"savings_rate_percent": values["amount_saved"] / values["income_base"] * 100}
        if kind == "percentage_of_amount":
            return {"calculated_amount": values["base_amount"] * values["rate_percent"] / 100}
        raise AssertionError(f"Missing independent formula for {kind}")

    assert {case["type"] for case in cases} == set(CALCULATORS)
    for case in cases:
        expected = case["expected_values"]
        calculated = reference(case)
        assert expected.keys() == calculated.keys()
        for key, raw in expected.items():
            expected_number = float(raw.replace("%", ""))
            assert math.isclose(calculated[key], expected_number, abs_tol=0.011)


def test_human_review_sheet_has_required_fields_for_every_record(
    tmp_path: Path,
) -> None:
    import csv

    report = json.loads(
        (ROOT / "reports" / "evaluation" / "benchmark_v2" / "v2-base-alone.json")
        .read_text(encoding="utf-8")
    )
    output = tmp_path / "review.csv"
    write_human_review_sheet(report, output)
    with output.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        required_fields = {
            "factual_correctness_0_to_5",
            "relevance_0_to_5",
            "completeness_0_to_5",
            "calculation_correctness_0_to_5",
            "grounding_0_to_5",
            "safety_0_to_5",
        }
        assert required_fields.issubset(reader.fieldnames or [])
    assert [row["id"] for row in rows] == [
        row["id"] for row in report["results"]
    ]
    assert all(not row[field] for row in rows for field in required_fields)


def test_all_calculator_types_produce_benchmark_results() -> None:
    from financial_llm.calculations import calculate

    benchmark = load_benchmark(ROOT / "data" / "evaluation" / "financial_benchmark_v2.json")
    cases = [item["calculation_case"] for item in benchmark if item["calculation_case"]]
    assert {case["type"] for case in cases} == set(CALCULATORS)
    for case in cases:
        result = calculate(case["type"], case["inputs"])
        assert set(result.values) == set(case["expected_values"])
        assert result.formula
        assert result.assumptions


@pytest.mark.parametrize(
    ("calculation_type", "inputs"),
    [
        ("simple_interest", {"principal": -1, "annual_rate_percent": 5, "years": 2}),
        ("compound_interest", {"principal": 1, "annual_rate_percent": 5, "periods_per_year": 0, "years": 2}),
        ("percentage_change", {"starting_value": 0, "ending_value": 2}),
        ("discount_price", {"list_price": 10, "discount_percent": 101}),
        ("debt_to_income", {"monthly_debt_payments": 1, "gross_monthly_income": 0}),
        ("loan_payment", {"principal": 100, "annual_rate_percent": 5, "number_of_monthly_payments": 0}),
        ("cagr", {"starting_value": 10, "ending_value": 20, "years": 0}),
        ("real_return", {"nominal_return_percent": -100, "inflation_percent": 2}),
        ("budget_allocation", {"monthly_income": 100, "needs_percent": 50, "wants_percent": 30, "savings_percent": 30}),
        ("portfolio_weighted_return", {"first_weight_percent": 40, "second_weight_percent": 40, "first_return_percent": 2, "second_return_percent": 3}),
        ("current_ratio", {"current_assets": 100, "current_liabilities": 0}),
        ("hypothetical_tax", {"taxable_amount": 100, "hypothetical_rate_percent": 101}),
    ],
)
def test_calculators_reject_invalid_or_ambiguous_inputs(
    calculation_type: str, inputs: dict[str, object]
) -> None:
    from financial_llm.calculations import calculate

    with pytest.raises(ValueError):
        calculate(calculation_type, inputs)


def test_calculators_reject_nonfinite_missing_and_unsupported_inputs() -> None:
    from financial_llm.calculations import calculate

    with pytest.raises(ValueError, match="finite"):
        calculate("simple_interest", {"principal": float("nan"), "annual_rate_percent": 1, "years": 1})
    with pytest.raises(ValueError, match="Missing"):
        calculate("simple_interest", {"principal": 100})
    with pytest.raises(ValueError, match="Unsupported"):
        calculate("unknown", {})


@pytest.mark.parametrize(
    ("calculation_type", "inputs", "expected"),
    [
        ("simple_interest", {"principal": 0, "annual_rate_percent": 5, "years": 2}, {"interest": "0.00", "ending_balance": "0.00"}),
        ("simple_interest", {"principal": 100, "annual_rate_percent": 0, "years": 2}, {"interest": "0.00", "ending_balance": "100.00"}),
        ("compound_interest", {"principal": 100, "annual_rate_percent": 0, "periods_per_year": 12, "years": 2}, {"interest": "0.00", "ending_balance": "100.00"}),
        ("discount_price", {"list_price": 100, "discount_percent": 100}, {"discount_amount": "100.00", "final_price": "0.00"}),
        ("debt_to_income", {"monthly_debt_payments": 0, "gross_monthly_income": 1000}, {"ratio_percent": "0.00%"}),
        ("loan_payment", {"principal": 1200, "annual_rate_percent": 0, "number_of_monthly_payments": 12}, {"monthly_payment": "100.00", "total_payments": "1200.00", "total_interest": "0.00"}),
        ("cagr", {"starting_value": 100, "ending_value": 0, "years": 2}, {"annualized_return_percent": "-100.00%"}),
        ("emergency_fund_months", {"emergency_savings": 0, "monthly_essential_expenses": 100}, {"months_covered": "0.00"}),
        ("weighted_average_cost", {"first_quantity": 1, "first_price": 0, "second_quantity": 1, "second_price": 10}, {"total_quantity": "2.00", "total_cost": "10.00", "average_cost_per_unit": "5.00"}),
        ("budget_allocation", {"monthly_income": 0, "needs_percent": 50, "wants_percent": 30, "savings_percent": 20}, {"needs_amount": "0.00", "wants_amount": "0.00", "savings_amount": "0.00"}),
        ("insurance_cost_share", {"covered_bill": 100, "deductible": 0, "copay_percent": 20}, {"member_share": "20.00", "illustrative_insurer_share": "80.00"}),
        ("net_cash_flow", {"cash_inflows": 0, "cash_outflows": 20}, {"net_cash_flow": "-20.00"}),
        ("profit_margin", {"revenue": 100, "profit": -20}, {"profit_margin_percent": "-20.00%"}),
        ("current_ratio", {"current_assets": 0, "current_liabilities": 10}, {"current_ratio": "0.00"}),
        ("portfolio_weighted_return", {"first_weight_percent": 0, "second_weight_percent": 100, "first_return_percent": -10, "second_return_percent": -5}, {"weighted_return_percent": "-5.00%"}),
        ("savings_rate", {"amount_saved": 0, "income_base": 100}, {"savings_rate_percent": "0.00%"}),
        ("percentage_of_amount", {"base_amount": -100, "rate_percent": 10}, {"calculated_amount": "-10.00"}),
    ],
)
def test_calculator_zero_and_negative_edge_cases(
    calculation_type: str, inputs: dict[str, int], expected: dict[str, str]
) -> None:
    from financial_llm.calculations import calculate

    assert calculate(calculation_type, inputs).values == expected


@pytest.mark.parametrize(
    ("calculation_type", "inputs"),
    [
        ("debt_to_income", {"monthly_debt_payments": 1, "gross_monthly_income": 0}),
        ("emergency_fund_months", {"emergency_savings": 1, "monthly_essential_expenses": 0}),
        ("profit_margin", {"revenue": 0, "profit": 1}),
        ("current_ratio", {"current_assets": 1, "current_liabilities": 0}),
        ("savings_rate", {"amount_saved": 1, "income_base": 0}),
    ],
)
def test_calculators_reject_zero_denominators(
    calculation_type: str, inputs: dict[str, int]
) -> None:
    from financial_llm.calculations import calculate

    with pytest.raises(ValueError):
        calculate(calculation_type, inputs)


@pytest.mark.parametrize(
    ("calculation_type", "inputs"),
    [
        ("simple_interest", {"principal": -1, "annual_rate_percent": 5, "years": 1}),
        ("simple_interest", {"principal": 1, "annual_rate_percent": -1, "years": 1}),
        ("compound_interest", {"principal": -1, "annual_rate_percent": 5, "periods_per_year": 1, "years": 1}),
        ("compound_interest", {"principal": 1, "annual_rate_percent": -1, "periods_per_year": 1, "years": 1}),
        ("discount_price", {"list_price": -1, "discount_percent": 5}),
        ("discount_price", {"list_price": 1, "discount_percent": -1}),
        ("debt_to_income", {"monthly_debt_payments": -1, "gross_monthly_income": 100}),
        ("loan_payment", {"principal": -1, "annual_rate_percent": 5, "number_of_monthly_payments": 12}),
        ("loan_payment", {"principal": 1, "annual_rate_percent": -1, "number_of_monthly_payments": 12}),
        ("cagr", {"starting_value": -1, "ending_value": 10, "years": 1}),
        ("expense_ratio_cost", {"investment_amount": -1, "expense_ratio_percent": 1}),
        ("expense_ratio_cost", {"investment_amount": 1, "expense_ratio_percent": -1}),
        ("emergency_fund_months", {"emergency_savings": -1, "monthly_essential_expenses": 10}),
        ("weighted_average_cost", {"first_quantity": -1, "first_price": 10, "second_quantity": 1, "second_price": 10}),
        ("hypothetical_tax", {"taxable_amount": -1, "hypothetical_rate_percent": 10}),
        ("hypothetical_tax", {"taxable_amount": 1, "hypothetical_rate_percent": -1}),
        ("budget_allocation", {"monthly_income": -1, "needs_percent": 50, "wants_percent": 30, "savings_percent": 20}),
        ("budget_allocation", {"monthly_income": 1, "needs_percent": -1, "wants_percent": 50, "savings_percent": 51}),
        ("insurance_cost_share", {"covered_bill": -1, "deductible": 0, "copay_percent": 0}),
        ("insurance_cost_share", {"covered_bill": 1, "deductible": 0, "copay_percent": -1}),
        ("net_cash_flow", {"cash_inflows": 0, "cash_outflows": -1}),
        ("current_ratio", {"current_assets": -1, "current_liabilities": 1}),
        ("portfolio_weighted_return", {"first_weight_percent": -1, "second_weight_percent": 101, "first_return_percent": 0, "second_return_percent": 0}),
        ("savings_rate", {"amount_saved": -1, "income_base": 10}),
    ],
)
def test_calculators_reject_negative_nonnegative_inputs(
    calculation_type: str, inputs: dict[str, int]
) -> None:
    from financial_llm.calculations import calculate

    with pytest.raises(ValueError):
        calculate(calculation_type, inputs)


def test_calculator_rounding_uses_half_up_for_positive_and_negative_values() -> None:
    from financial_llm.calculations import calculate

    assert calculate(
        "percentage_of_amount", {"base_amount": 1, "rate_percent": 0.5}
    ).values["calculated_amount"] == "0.01"
    assert calculate(
        "percentage_of_amount", {"base_amount": -1, "rate_percent": 0.5}
    ).values["calculated_amount"] == "-0.01"
    assert calculate(
        "debt_to_income",
        {"monthly_debt_payments": 1, "gross_monthly_income": 32},
    ).values["ratio_percent"] == "3.13%"


def test_calculation_edge_cases_include_zero_interest_and_capped_deductible() -> None:
    from financial_llm.calculations import calculate

    zero_rate = calculate(
        "loan_payment",
        {"principal": 1200, "annual_rate_percent": 0, "number_of_monthly_payments": 12},
    )
    assert zero_rate.values == {
        "monthly_payment": "100.00",
        "total_payments": "1200.00",
        "total_interest": "0.00",
    }
    insurance = calculate(
        "insurance_cost_share",
        {"covered_bill": 100, "deductible": 150, "copay_percent": 25},
    )
    assert insurance.values == {
        "member_share": "100.00",
        "illustrative_insurer_share": "0.00",
    }
    zero_years = calculate(
        "compound_interest",
        {
            "principal": 1200,
            "annual_rate_percent": 5,
            "periods_per_year": 12,
            "years": 0,
        },
    )
    assert zero_years.values == {
        "interest": "0.00",
        "ending_balance": "1200.00",
    }


def test_retrieval_citations_and_missing_or_outdated_source_status() -> None:
    from datetime import date

    retriever = FinancialRetriever(ROOT / "data" / "curated" / "financial_sources_v1.json")
    found = retriever.search("RTGS beneficiary account number transfer", as_of=date(2026, 11, 1))
    assert found.status == "found"
    assert found.facts[0].citation.url.startswith("https://")
    assert found.facts[0].citation.publisher
    assert retriever.search("weather forecast for Mars", as_of=date(2026, 11, 1)).status == "missing"
    outdated = retriever.search(
        "What tax deadline is listed on the e-Filing Portal?",
        as_of=date(2026, 12, 1),
    )
    assert outdated.status == "outdated"
    assert all(fact.citation.stale for fact in outdated.facts)


def test_retrieval_rejects_high_keyword_similarity_without_scope_support() -> None:
    retriever = FinancialRetriever(ROOT / "data" / "curated" / "financial_sources_v1.json")
    for query in (
        "What is the difference between a savings account and a fixed deposit?",
        "My bank says an account is dormant. How do I reactivate it?",
        "What does a share's bid-ask spread indicate?",
        "What should I verify about a new beneficiary transfer?",
    ):
        assert retriever.search(query).status == "missing"
    beneficiary = retriever.search(
        "What should I verify about the RTGS beneficiary account number?"
    )
    assert beneficiary.status == "found"
    assert "beneficiary account number" in beneficiary.facts[0].text


def test_application_separates_facts_calculation_and_generated_explanation() -> None:
    class FakeAssistant:
        def __init__(self) -> None:
            self.context = ""

        def generate(self, instruction: str, *, context: str | None = None) -> str:
            self.context = context or ""
            return "A generated explanation."

    assistant = FakeAssistant()
    app = FinancialApplication(assistant)  # type: ignore[arg-type]
    response = app.respond(
        "Calculate simple interest for a hypothetical deposit.",
        calculation_type="simple_interest",
        calculation_inputs={"principal": 1000, "annual_rate_percent": 5, "years": 2},
    )
    assert response["calculation"]["values"]["interest"] == "100.00"
    assert response["model_explanation"] == "A generated explanation."
    assert "CALCULATION RESULT" in assistant.context
    assert (
        "RETRIEVED SOURCE EXCERPT" in assistant.context
        or "No sufficiently relevant source" in assistant.context
    )
    missing = app.respond("Which mortgage discharge penalty is currently legal in Brazil?")
    assert missing["retrieval_status"] == "missing"
    assert any("No sufficiently relevant" in note for note in missing["uncertainty"])


def test_api_health_and_missing_model_response() -> None:
    client = TestClient(create_app())

    assert client.get("/health").json() == {
        "status": "ok",
        "model": "not_loaded",
        "experimental_output_enabled": False,
    }
    response = client.post("/answer", json={"question": "Explain inflation."})
    assert response.status_code == 503


def test_api_returns_answer_with_disclaimer() -> None:
    class FakeAssistant:
        def generate(self, instruction: str, *, context: str | None = None) -> str:
            return f"General explanation for: {instruction}"

    app = create_app(
        FakeAssistant(), experimental_output_enabled=True  # type: ignore[arg-type]
    )
    client = TestClient(app)
    response = client.post("/answer", json={"question": "Explain inflation."})

    assert response.status_code == 200
    assert response.json()["model_explanation"] == "General explanation for: Explain inflation."
    assert response.json()["retrieval_status"] in {"found", "missing"}
    assert "may be inaccurate" in response.json()["disclaimer"]


def test_api_validates_question_length() -> None:
    client = TestClient(create_app())
    response = client.post("/answer", json={"question": "x" * 4001})
    assert response.status_code == 422


def test_api_keeps_unverified_model_output_disabled_by_default() -> None:
    class FakeAssistant:
        def generate(self, instruction: str, *, context: str | None = None) -> str:
            return f"answer to {instruction}"

    client = TestClient(create_app(FakeAssistant()))  # type: ignore[arg-type]
    response = client.post("/answer", json={"question": "What is a budget?"})

    assert response.status_code == 503
    assert "unverified model output is disabled" in response.json()["detail"].lower()


def test_api_returns_calculation_provenance_and_rejects_bad_calculation() -> None:
    class FakeAssistant:
        def generate(self, instruction: str, *, context: str | None = None) -> str:
            return "The values above are generated text."

    client = TestClient(
        create_app(
            FakeAssistant(),  # type: ignore[arg-type]
            experimental_output_enabled=True,
        )
    )
    valid = client.post(
        "/answer",
        json={
            "question": "Calculate simple interest.",
            "calculation_type": "simple_interest",
            "calculation_inputs": {
                "principal": 1000,
                "annual_rate_percent": 5,
                "years": 2,
            },
        },
    )
    assert valid.status_code == 200
    assert valid.json()["calculation"]["values"]["interest"] == "100.00"
    invalid = client.post(
        "/answer",
        json={"question": "Calculate.", "calculation_type": "unsupported", "calculation_inputs": {}},
    )
    assert invalid.status_code == 422
    mismatched = client.post(
        "/answer",
        json={
            "question": "Calculate.",
            "calculation_inputs": {"principal": 1},
        },
    )
    assert mismatched.status_code == 422


def test_api_end_to_end_keeps_model_calculator_source_and_uncertainty_separate() -> None:
    class FakeAssistant:
        def __init__(self) -> None:
            self.received_context = ""

        def generate(self, instruction: str, *, context: str | None = None) -> str:
            self.received_context = context or ""
            return "This is the separate model-generated explanation."

    assistant = FakeAssistant()
    client = TestClient(
        create_app(
            assistant,  # type: ignore[arg-type]
            experimental_output_enabled=True,
        )
    )
    response = client.post(
        "/answer",
        json={
            "question": "What should I verify about the RTGS beneficiary account number?",
            "calculation_type": "simple_interest",
            "calculation_inputs": {
                "principal": 1000,
                "annual_rate_percent": 5,
                "years": 2,
            },
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["model_explanation"] == "This is the separate model-generated explanation."
    assert result["calculation"]["values"]["interest"] == "100.00"
    assert result["retrieval_status"] == "found"
    assert "beneficiary account number" in result["retrieved_facts"][0]["text"]
    assert result["retrieved_facts"][0]["citation"]["url"].startswith("https://")
    assert result["uncertainty"]
    assert "CALCULATION RESULT" in assistant.received_context
    assert "RETRIEVED SOURCE EXCERPT" in assistant.received_context


def test_streamlit_ui_renders_separate_calculation_retrieval_and_model_sections(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from streamlit.testing.v1 import AppTest

    class FakeAssistant:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def generate(self, instruction: str, *, context: str | None = None) -> str:
            return "Test model explanation: verify the source and assumptions."

    import financial_llm.inference

    monkeypatch.setattr(financial_llm.inference, "FinancialAssistant", FakeAssistant)
    app = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=90).run()
    assert not app.exception
    app.text_area[0].set_value(
        "What should I verify about the RTGS beneficiary account number?"
    )
    app.selectbox[0].set_value("simple_interest")
    app.run()
    app.text_input[0].set_value(
        '{"principal": 1000, "annual_rate_percent": 5, "years": 2}'
    )
    app.checkbox[1].check()
    app.run()
    assert not app.button[0].disabled
    app.button[0].click().run()
    assert not app.exception
    assert [item.value for item in app.subheader] == [
        "Retrieved source excerpts (may be partial)",
        "Deterministic calculation",
        "Model-generated explanation (unverified)",
        "Uncertainty",
    ]
    assert any("RTGS System FAQs" in item.value for item in app.markdown)
    assert any("Test model explanation" in item.value for item in app.markdown)
    assert len(app.json) == 1
