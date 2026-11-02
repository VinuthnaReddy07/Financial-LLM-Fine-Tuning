import json

# Financial question-answer examples
financial_data = [
    {
        "instruction": "What is simple interest?",
        "response": "Simple interest is calculated only on the original principal amount. It does not include previously earned interest."
    },
    {
        "instruction": "What is compound interest?",
        "response": "Compound interest is calculated on the original principal as well as the interest accumulated over previous periods."
    },
    {
        "instruction": "What is inflation?",
        "response": "Inflation is the general increase in the prices of goods and services over time. It reduces the purchasing power of money."
    },
    {
        "instruction": "What is a credit score?",
        "response": "A credit score is a numerical measure of a person's credit history. Lenders may use it to assess creditworthiness."
    },
    {
        "instruction": "What is a savings account?",
        "response": "A savings account is a bank account used to deposit money securely while earning interest according to the bank's terms."
    },
    {
        "instruction": "What is a fixed deposit?",
        "response": "A fixed deposit is a financial product where money is deposited with a bank for a specified period at an agreed interest rate."
    },
    {
        "instruction": "What is a loan?",
        "response": "A loan is money borrowed from a lender that must generally be repaid over an agreed period, usually with interest."
    },
    {
        "instruction": "What is diversification?",
        "response": "Diversification means spreading investments across different assets to reduce dependence on the performance of a single investment."
    },
    {
        "instruction": "What is a stock?",
        "response": "A stock represents partial ownership in a company. Stock prices can rise or fall depending on market conditions and company performance."
    },
    {
        "instruction": "What is a bond?",
        "response": "A bond is a debt instrument through which an investor lends money to an issuer in exchange for interest payments and repayment under agreed terms."
    }
]

# Save the dataset as JSON
with open("data/financial_dataset.json", "w") as file:
    json.dump(financial_data, file, indent=4)

print("Financial dataset created successfully!")
print("Total examples:", len(financial_data))