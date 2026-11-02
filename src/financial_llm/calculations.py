from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from typing import Any, Callable

CENT = Decimal("0.01")
ZERO = Decimal("0")
HUNDRED = Decimal("100")


@dataclass(frozen=True)
class CalculationResult:
    calculation_type: str
    values: dict[str, str]
    formula: str
    assumptions: list[str]
    units: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _decimal(inputs: dict[str, Any], key: str) -> Decimal:
    if key not in inputs:
        raise ValueError(f"Missing required input: {key}")
    try:
        value = Decimal(str(inputs[key]))
    except (InvalidOperation, ValueError, TypeError) as error:
        raise ValueError(f"{key} must be a finite number.") from error
    if not value.is_finite():
        raise ValueError(f"{key} must be a finite number.")
    return value


def _positive(value: Decimal, name: str, *, allow_zero: bool = True) -> Decimal:
    if value < ZERO or (not allow_zero and value == ZERO):
        comparator = "positive" if not allow_zero else "non-negative"
        raise ValueError(f"{name} must be {comparator}.")
    return value


def _integer(inputs: dict[str, Any], key: str, *, minimum: int = 1) -> int:
    value = _decimal(inputs, key)
    if value != value.to_integral_value() or value < minimum:
        raise ValueError(f"{key} must be an integer of at least {minimum}.")
    return int(value)


def _money(value: Decimal) -> str:
    return str(value.quantize(CENT, rounding=ROUND_HALF_UP))


def _percentage(value: Decimal) -> str:
    return f"{value.quantize(CENT, rounding=ROUND_HALF_UP)}%"


def _result(
    name: str,
    values: dict[str, Decimal],
    formula: str,
    assumptions: list[str],
    units: str = "currency units unless specified",
) -> CalculationResult:
    formatted = {
        key: _percentage(value) if key.endswith("_percent") else _money(value)
        for key, value in values.items()
    }
    return CalculationResult(name, formatted, formula, assumptions, units)


def simple_interest(inputs: dict[str, Any]) -> CalculationResult:
    principal = _positive(_decimal(inputs, "principal"), "principal")
    rate = _positive(_decimal(inputs, "annual_rate_percent"), "annual_rate_percent")
    years = _positive(_decimal(inputs, "years"), "years")
    interest = principal * rate / HUNDRED * years
    return _result(
        "simple_interest",
        {"interest": interest, "ending_balance": principal + interest},
        "I = P × (r / 100) × t; A = P + I",
        ["Annual simple rate; no fees, taxes, deposits, or withdrawals."],
    )


def compound_interest(inputs: dict[str, Any]) -> CalculationResult:
    principal = _positive(
        _decimal(inputs, "principal"), "principal", allow_zero=False
    )
    rate = _positive(_decimal(inputs, "annual_rate_percent"), "annual_rate_percent")
    periods_per_year = _integer(inputs, "periods_per_year")
    years = _integer(inputs, "years", minimum=0)
    with localcontext() as context:
        context.prec = 40
        factor = Decimal(1) + rate / HUNDRED / periods_per_year
        balance = principal * (factor ** (periods_per_year * years))
    return _result(
        "compound_interest",
        {"interest": balance - principal, "ending_balance": balance},
        "A = P × (1 + r / n) ** (n × t); I = A − P",
        [
            "Fixed nominal annual rate compounded at equal intervals.",
            "No fees, taxes, deposits, or withdrawals.",
        ],
    )


def percentage_change(inputs: dict[str, Any]) -> CalculationResult:
    starting = _decimal(inputs, "starting_value")
    ending = _decimal(inputs, "ending_value")
    if starting == ZERO:
        raise ValueError("starting_value cannot be zero for percentage change.")
    change = ending - starting
    return _result(
        "percentage_change",
        {"absolute_change": change, "change_percent": change / starting * HUNDRED},
        "Change = ending value − starting value; % change = change / starting value × 100",
        ["The starting value is non-zero; this is a change, not an investment return after costs."],
        "same units as inputs; percentage change",
    )


def discount_price(inputs: dict[str, Any]) -> CalculationResult:
    price = _positive(_decimal(inputs, "list_price"), "list_price")
    rate = _positive(_decimal(inputs, "discount_percent"), "discount_percent")
    if rate > HUNDRED:
        raise ValueError("discount_percent cannot exceed 100.")
    discount = price * rate / HUNDRED
    return _result(
        "discount_price",
        {"discount_amount": discount, "final_price": price - discount},
        "Discount = list price × discount rate; final price = list price − discount",
        ["Excludes tax, shipping, and other fees."],
    )


def debt_to_income(inputs: dict[str, Any]) -> CalculationResult:
    debt = _positive(
        _decimal(inputs, "monthly_debt_payments"), "monthly_debt_payments"
    )
    income = _positive(
        _decimal(inputs, "gross_monthly_income"),
        "gross_monthly_income",
        allow_zero=False,
    )
    return _result(
        "debt_to_income",
        {"ratio_percent": debt / income * HUNDRED},
        "Monthly debt payments / gross monthly income × 100",
        ["Uses only the debt payments and gross income supplied; lender definitions can differ."],
        "percentage",
    )


def loan_payment(inputs: dict[str, Any]) -> CalculationResult:
    principal = _positive(
        _decimal(inputs, "principal"), "principal", allow_zero=False
    )
    annual_rate = _positive(
        _decimal(inputs, "annual_rate_percent"), "annual_rate_percent"
    )
    payments = _integer(inputs, "number_of_monthly_payments")
    monthly_rate = annual_rate / HUNDRED / Decimal(12)
    if monthly_rate == ZERO:
        payment = principal / payments
    else:
        with localcontext() as context:
            context.prec = 40
            factor = (Decimal(1) + monthly_rate) ** payments
            payment = principal * monthly_rate * factor / (factor - Decimal(1))
    total = payment * payments
    return _result(
        "loan_payment",
        {"monthly_payment": payment, "total_payments": total, "total_interest": total - principal},
        "EMI = P × i × (1 + i) ** n / ((1 + i) ** n − 1); i = annual rate / 12",
        [
            "Fixed annual nominal rate divided into monthly periods.",
            "Equal end-of-month payments; excludes fees, taxes, insurance, and rounding by a lender.",
        ],
    )


def cagr(inputs: dict[str, Any]) -> CalculationResult:
    starting = _positive(
        _decimal(inputs, "starting_value"), "starting_value", allow_zero=False
    )
    ending = _positive(_decimal(inputs, "ending_value"), "ending_value")
    years = _integer(inputs, "years")
    with localcontext() as context:
        context.prec = 40
        rate = (ending / starting) ** (Decimal(1) / years) - Decimal(1)
    return _result(
        "cagr",
        {"annualized_return_percent": rate * HUNDRED},
        "CAGR = (ending value / starting value) ** (1 / years) − 1",
        ["Annualized geometric rate; excludes contributions, withdrawals, costs, and taxes."],
        "percentage per year",
    )


def real_return(inputs: dict[str, Any]) -> CalculationResult:
    nominal = _decimal(inputs, "nominal_return_percent")
    inflation = _decimal(inputs, "inflation_percent")
    if nominal <= -HUNDRED or inflation <= -HUNDRED:
        raise ValueError("Return and inflation rates must each be greater than -100%.")
    exact = (
        (Decimal(1) + nominal / HUNDRED)
        / (Decimal(1) + inflation / HUNDRED)
        - Decimal(1)
    ) * HUNDRED
    approximate = nominal - inflation
    return _result(
        "real_return",
        {"real_return_percent": exact, "approximate_real_return_percent": approximate},
        "Exact real return = ((1 + nominal return) / (1 + inflation) − 1) × 100",
        ["Uses the supplied rates for the same period; excludes tax, fees, and timing effects."],
        "percentage",
    )


def expense_ratio_cost(inputs: dict[str, Any]) -> CalculationResult:
    assets = _positive(_decimal(inputs, "investment_amount"), "investment_amount")
    rate = _positive(_decimal(inputs, "expense_ratio_percent"), "expense_ratio_percent")
    if rate > HUNDRED:
        raise ValueError("expense_ratio_percent cannot exceed 100.")
    return _result(
        "expense_ratio_cost",
        {"annualized_cost_estimate": assets * rate / HUNDRED},
        "Illustrative annual cost = investment amount × expense ratio / 100",
        ["Assumes the investment amount stays constant for one year; actual fund costs and returns vary."],
    )


def emergency_fund_months(inputs: dict[str, Any]) -> CalculationResult:
    savings = _positive(
        _decimal(inputs, "emergency_savings"), "emergency_savings"
    )
    expenses = _positive(
        _decimal(inputs, "monthly_essential_expenses"),
        "monthly_essential_expenses",
        allow_zero=False,
    )
    return _result(
        "emergency_fund_months",
        {"months_covered": savings / expenses},
        "Emergency savings / monthly essential expenses",
        ["Coverage estimate only; actual needs depend on circumstances and expense changes."],
        "months",
    )


def weighted_average_cost(inputs: dict[str, Any]) -> CalculationResult:
    first_quantity = _positive(
        _decimal(inputs, "first_quantity"), "first_quantity", allow_zero=False
    )
    first_price = _positive(_decimal(inputs, "first_price"), "first_price")
    second_quantity = _positive(
        _decimal(inputs, "second_quantity"), "second_quantity", allow_zero=False
    )
    second_price = _positive(_decimal(inputs, "second_price"), "second_price")
    quantity = first_quantity + second_quantity
    average = (
        first_quantity * first_price + second_quantity * second_price
    ) / quantity
    return _result(
        "weighted_average_cost",
        {
            "total_quantity": quantity,
            "total_cost": first_quantity * first_price + second_quantity * second_price,
            "average_cost_per_unit": average,
        },
        "Weighted average = total purchase cost / total quantity",
        ["Excludes brokerage, fees, taxes, corporate actions, and any sales."],
        "quantity, currency units, currency units per unit",
    )


def hypothetical_tax(inputs: dict[str, Any]) -> CalculationResult:
    amount = _positive(_decimal(inputs, "taxable_amount"), "taxable_amount")
    rate = _positive(_decimal(inputs, "hypothetical_rate_percent"), "hypothetical_rate_percent")
    if rate > HUNDRED:
        raise ValueError("hypothetical_rate_percent cannot exceed 100.")
    tax = amount * rate / HUNDRED
    return _result(
        "hypothetical_tax",
        {"illustrative_tax": tax, "amount_after_illustrative_tax": amount - tax},
        "Illustration = supplied amount × supplied hypothetical rate / 100",
        ["Arithmetic illustration only; not a current tax rate or tax liability calculation."],
    )


def budget_allocation(inputs: dict[str, Any]) -> CalculationResult:
    income = _positive(_decimal(inputs, "monthly_income"), "monthly_income")
    needs_rate = _positive(_decimal(inputs, "needs_percent"), "needs_percent")
    wants_rate = _positive(_decimal(inputs, "wants_percent"), "wants_percent")
    savings_rate = _positive(_decimal(inputs, "savings_percent"), "savings_percent")
    if needs_rate + wants_rate + savings_rate != HUNDRED:
        raise ValueError("Budget allocation percentages must sum to 100.")
    return _result(
        "budget_allocation",
        {
            "needs_amount": income * needs_rate / HUNDRED,
            "wants_amount": income * wants_rate / HUNDRED,
            "savings_amount": income * savings_rate / HUNDRED,
        },
        "Each allocation = monthly income × its supplied percentage / 100",
        ["Illustrative allocation only; supplied percentages are not financial advice."],
    )


def insurance_cost_share(inputs: dict[str, Any]) -> CalculationResult:
    bill = _positive(
        _decimal(inputs, "covered_bill"), "covered_bill", allow_zero=False
    )
    deductible = _positive(_decimal(inputs, "deductible"), "deductible")
    copay_rate = _positive(_decimal(inputs, "copay_percent"), "copay_percent")
    if copay_rate > HUNDRED:
        raise ValueError("copay_percent cannot exceed 100.")
    member_deductible = min(bill, deductible)
    remaining = bill - member_deductible
    copay = remaining * copay_rate / HUNDRED
    member_share = member_deductible + copay
    return _result(
        "insurance_cost_share",
        {
            "member_share": member_share,
            "illustrative_insurer_share": bill - member_share,
        },
        "Member share = min(bill, deductible) + copay rate × (bill − deductible)",
        [
            "Hypothetical covered bill; assumes copay applies after the deductible.",
            "Actual coverage, exclusions, limits, and cost-sharing order depend on policy terms.",
        ],
    )


def net_cash_flow(inputs: dict[str, Any]) -> CalculationResult:
    inflows = _positive(_decimal(inputs, "cash_inflows"), "cash_inflows")
    outflows = _positive(_decimal(inputs, "cash_outflows"), "cash_outflows")
    return _result(
        "net_cash_flow",
        {"net_cash_flow": inflows - outflows},
        "Net cash flow = cash inflows − cash outflows",
        ["Uses only the supplied period and cash-flow amounts."],
    )


def profit_margin(inputs: dict[str, Any]) -> CalculationResult:
    revenue = _positive(
        _decimal(inputs, "revenue"), "revenue", allow_zero=False
    )
    profit = _decimal(inputs, "profit")
    return _result(
        "profit_margin",
        {"profit_margin_percent": profit / revenue * HUNDRED},
        "Profit margin = profit / revenue × 100",
        ["Uses the supplied definition of profit and revenue for the same period."],
        "percentage",
    )


def current_ratio(inputs: dict[str, Any]) -> CalculationResult:
    current_assets = _positive(
        _decimal(inputs, "current_assets"), "current_assets"
    )
    current_liabilities = _positive(
        _decimal(inputs, "current_liabilities"),
        "current_liabilities",
        allow_zero=False,
    )
    ratio = current_assets / current_liabilities
    return _result(
        "current_ratio",
        {"current_ratio": ratio},
        "Current ratio = current assets / current liabilities",
        ["Uses the supplied balance-sheet values; does not determine solvency by itself."],
        "ratio",
    )


def portfolio_weighted_return(inputs: dict[str, Any]) -> CalculationResult:
    first_weight = _positive(
        _decimal(inputs, "first_weight_percent"), "first_weight_percent"
    )
    second_weight = _positive(
        _decimal(inputs, "second_weight_percent"), "second_weight_percent"
    )
    if first_weight + second_weight != HUNDRED:
        raise ValueError("The two portfolio weights must sum to 100.")
    first_return = _decimal(inputs, "first_return_percent")
    second_return = _decimal(inputs, "second_return_percent")
    result = (
        first_weight * first_return + second_weight * second_return
    ) / HUNDRED
    return _result(
        "portfolio_weighted_return",
        {"weighted_return_percent": result},
        "Portfolio return = sum(weight percentage × component return) / 100",
        ["Assumes the supplied weights sum to 100%; excludes rebalancing, fees, and taxes."],
        "percentage",
    )


def savings_rate(inputs: dict[str, Any]) -> CalculationResult:
    saved = _positive(_decimal(inputs, "amount_saved"), "amount_saved")
    income = _positive(
        _decimal(inputs, "income_base"), "income_base", allow_zero=False
    )
    return _result(
        "savings_rate",
        {"savings_rate_percent": saved / income * HUNDRED},
        "Savings rate = amount saved / specified income base × 100",
        ["The meaning of the income base (gross, net, or other) must be defined by the user."],
        "percentage",
    )


def percentage_of_amount(inputs: dict[str, Any]) -> CalculationResult:
    amount = _decimal(inputs, "base_amount")
    rate = _decimal(inputs, "rate_percent")
    return _result(
        "percentage_of_amount",
        {"calculated_amount": amount * rate / HUNDRED},
        "Calculated amount = base amount × supplied rate / 100",
        ["Arithmetic only; the supplied percentage is not checked against any current rule."],
    )


CALCULATORS: dict[str, Callable[[dict[str, Any]], CalculationResult]] = {
    "simple_interest": simple_interest,
    "compound_interest": compound_interest,
    "percentage_change": percentage_change,
    "discount_price": discount_price,
    "debt_to_income": debt_to_income,
    "loan_payment": loan_payment,
    "cagr": cagr,
    "real_return": real_return,
    "expense_ratio_cost": expense_ratio_cost,
    "emergency_fund_months": emergency_fund_months,
    "weighted_average_cost": weighted_average_cost,
    "hypothetical_tax": hypothetical_tax,
    "budget_allocation": budget_allocation,
    "insurance_cost_share": insurance_cost_share,
    "net_cash_flow": net_cash_flow,
    "profit_margin": profit_margin,
    "current_ratio": current_ratio,
    "portfolio_weighted_return": portfolio_weighted_return,
    "savings_rate": savings_rate,
    "percentage_of_amount": percentage_of_amount,
}


def calculate(calculation_type: str, inputs: dict[str, Any]) -> CalculationResult:
    if not isinstance(inputs, dict):
        raise ValueError("inputs must be an object of named numeric values.")
    calculator = CALCULATORS.get(calculation_type)
    if calculator is None:
        raise ValueError(
            f"Unsupported calculation type: {calculation_type}. "
            f"Supported types: {', '.join(sorted(CALCULATORS))}."
        )
    return calculator(inputs)
