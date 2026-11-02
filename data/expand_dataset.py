
import json

additional_data = [
    {
        "instruction": "What is annual percentage rate (APR)?",
        "response": "APR represents the yearly cost of borrowing, expressed as a percentage. It can include the interest rate and certain borrowing fees."
    },
    {
        "instruction": "What is annual percentage yield (APY)?",
        "response": "APY represents the effective yearly return on a deposit after accounting for compound interest."
    },
    {
        "instruction": "What is the difference between APR and APY?",
        "response": "APR generally describes the annual cost of borrowing, while APY describes the effective annual return after compounding. They are used for different financial purposes."
    },
    {
        "instruction": "What is a minimum balance?",
        "response": "A minimum balance is the lowest amount a bank requires an account holder to maintain under specified account conditions."
    },
    {
        "instruction": "What is a recurring deposit?",
        "response": "A recurring deposit is a savings product in which a person deposits a fixed amount at regular intervals for a specified period and earns interest according to the bank's terms."
    },
    {
        "instruction": "What is a mortgage?",
        "response": "A mortgage is a loan used to purchase property. The property generally serves as security for the loan."
    },
    {
        "instruction": "What is a secured loan?",
        "response": "A secured loan is a loan backed by collateral, such as a house or vehicle. The lender may have the right to claim the collateral if the borrower defaults, subject to applicable law."
    },
    {
        "instruction": "What is an unsecured loan?",
        "response": "An unsecured loan does not require specific collateral. Lenders generally evaluate factors such as credit history and income when assessing applications."
    },
    {
        "instruction": "What is loan default?",
        "response": "Loan default occurs when a borrower fails to meet the repayment obligations defined in the loan agreement."
    },
    {
        "instruction": "What is a credit report?",
        "response": "A credit report is a record of a person's credit history, which can include borrowing accounts, repayment history, and outstanding debts."
    },
    {
        "instruction": "What is a stock exchange?",
        "response": "A stock exchange is a regulated marketplace where eligible securities such as shares are bought and sold."
    },
    {
        "instruction": "What is a bull market?",
        "response": "A bull market is a market period characterized by generally rising prices and positive investor expectations."
    },
    {
        "instruction": "What is a bear market?",
        "response": "A bear market is a market period characterized by a significant and sustained decline in asset prices and generally negative investor sentiment."
    },
    {
        "instruction": "What is a capital gain?",
        "response": "A capital gain is the profit realized when an asset is sold for more than its purchase cost, subject to applicable cost adjustments and tax rules."
    },
    {
        "instruction": "What is a capital loss?",
        "response": "A capital loss occurs when an asset is sold for less than its relevant purchase cost."
    },
    {
        "instruction": "What is portfolio allocation?",
        "response": "Portfolio allocation is the distribution of investments among different asset categories, such as stocks, bonds, and cash."
    },
    {
        "instruction": "What is an exchange-traded fund?",
        "response": "An exchange-traded fund, or ETF, is an investment fund whose units trade on a stock exchange. It may hold a collection of assets such as stocks or bonds."
    },
    {
        "instruction": "What is an index fund?",
        "response": "An index fund is an investment fund designed to track the performance of a particular market index."
    },
    {
        "instruction": "What is expense ratio?",
        "response": "An expense ratio represents the annual operating expenses of an investment fund as a percentage of its assets."
    },
    {
        "instruction": "What is a market index?",
        "response": "A market index measures the performance of a selected group of securities and is often used to represent a segment of a financial market."
    },
    {
        "instruction": "What is investment volatility?",
        "response": "Volatility describes how much and how frequently an asset's price changes over a period. Higher volatility indicates larger price fluctuations."
    },
    {
        "instruction": "What is the relationship between risk and return?",
        "response": "Risk and return describe the uncertainty and potential reward of an investment. Investments with higher expected returns often involve higher risks, but higher returns are never guaranteed."
    },
    {
        "instruction": "What is asset allocation?",
        "response": "Asset allocation is the process of dividing investments among asset classes such as equities, bonds, and cash based on financial objectives and risk considerations."
    },
    {
        "instruction": "What is a liquid asset?",
        "response": "A liquid asset is an asset that can be converted into cash quickly with little loss in value."
    },
    {
        "instruction": "What is net worth?",
        "response": "Net worth is the difference between the total value of a person's assets and the total value of their liabilities."
    },
    {
        "instruction": "What is cash flow?",
        "response": "Cash flow is the movement of money into and out of a person, business, or organization during a specific period."
    },
    {
        "instruction": "What is a fixed expense?",
        "response": "A fixed expense is a recurring cost that generally remains consistent over a particular period, such as a monthly rent payment."
    },
    {
        "instruction": "What is a variable expense?",
        "response": "A variable expense is a cost that changes depending on usage, activity, or circumstances, such as electricity or grocery spending."
    },
    {
        "instruction": "What is debt-to-income ratio?",
        "response": "Debt-to-income ratio compares a person's recurring monthly debt payments with their gross monthly income. Lenders may use it when evaluating borrowing applications."
    },
    {
        "instruction": "What is a grace period?",
        "response": "A grace period is an additional period allowed under certain financial agreements before a payment becomes subject to specified penalties or interest."
    },
    {
        "instruction": "What is an overdraft?",
        "response": "An overdraft occurs when a bank account balance goes below zero because payments exceed available funds, when the bank permits the transaction."
    },
    {
        "instruction": "What is a financial liability?",
        "response": "A financial liability is an obligation to pay money or provide financial resources to another party, such as a loan or outstanding bill."
    },
    {
        "instruction": "What is an asset?",
        "response": "An asset is something of economic value owned or controlled by a person or organization, such as cash, property, or investments."
    },
    {
        "instruction": "What is a liability?",
        "response": "A liability is a financial obligation owed to another party, such as borrowed money, unpaid bills, or other debts."
    },
    {
        "instruction": "What is a balance sheet?",
        "response": "A balance sheet is a financial statement showing an organization's assets, liabilities, and equity at a particular point in time."
    },
    {
        "instruction": "What is revenue?",
        "response": "Revenue is the income generated from an organization's normal business activities before deducting expenses."
    },
    {
        "instruction": "What is profit?",
        "response": "Profit is the amount remaining when relevant expenses are deducted from revenue over a specified period."
    },
    {
        "instruction": "What is a financial goal?",
        "response": "A financial goal is a specific money-related objective, such as building savings, repaying debt, or funding education."
    },
    {
        "instruction": "Why is financial record keeping important?",
        "response": "Financial record keeping helps track income, expenses, debts, and savings. It also supports budgeting, financial planning, and reviewing financial decisions."
    },
    {
        "instruction": "What is the time value of money?",
        "response": "The time value of money is the principle that money available today can be worth more than the same amount received in the future because it can potentially earn a return."
    }
]

# Load the existing dataset
with open("data/financial_dataset.json", "r") as file:
    dataset = json.load(file)

# Avoid adding duplicate questions
existing_questions = {
    item["instruction"].strip().lower()
    for item in dataset
}

new_examples = []

for item in additional_data:
    question = item["instruction"].strip().lower()

    if question not in existing_questions:
        new_examples.append(item)
        existing_questions.add(question)

# Add new examples
dataset.extend(new_examples)

# Save the expanded dataset
with open("data/financial_dataset.json", "w") as file:
    json.dump(dataset, file, indent=4)

print("Dataset expansion completed!")
print("New examples added:", len(new_examples))
print("Total examples:", len(dataset))
