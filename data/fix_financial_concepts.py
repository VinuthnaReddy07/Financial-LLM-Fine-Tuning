import json

path = "data/financial_dataset.json"

with open(path, "r", encoding="utf-8") as file:
    dataset = json.load(file)

# Verify that the expected examples exist
assert dataset[153]["instruction"] == (
    "What is the difference between an ETF and a mutual fund?"
)

assert dataset[186]["instruction"] == "What is the Sharpe ratio?"

# Example 153: Improve conceptual precision
dataset[153]["instruction"] = (
    "What is the difference between an ETF and "
    "a traditional open-ended mutual fund?"
)

dataset[153]["response"] = (
    "An exchange-traded fund (ETF) is a pooled investment "
    "fund whose units are listed and traded on a stock exchange "
    "during market hours. A traditional open-ended mutual fund "
    "generally processes purchase and redemption requests at "
    "the applicable NAV calculated for the transaction. ETF "
    "market prices can differ from NAV, and investors may need "
    "a trading account to buy or sell ETF units. Both structures "
    "have investment risks and costs."
)

# Example 186: Clarify compatible measurement periods
dataset[186]["response"] = (
    "The Sharpe ratio measures an investment's excess return "
    "relative to its volatility. A common formula is "
    "(Portfolio Return - Risk-Free Rate) divided by the "
    "Standard Deviation of Portfolio Returns. The return, "
    "risk-free rate, and standard deviation should be measured "
    "over compatible periods. It is one way to compare "
    "risk-adjusted performance, but it depends on the selected "
    "period and assumptions."
)

# Save
with open(path, "w", encoding="utf-8") as file:
    json.dump(dataset, file, indent=4, ensure_ascii=False)

print("Financial concept improvements saved.")

for index in [153, 186]:
    print(f"\nExample {index}")
    print("Question:", dataset[index]["instruction"])
    print("Answer:", dataset[index]["response"])

print("\nTotal examples:", len(dataset))