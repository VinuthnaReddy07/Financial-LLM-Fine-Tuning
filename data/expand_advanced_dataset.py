import json
import os

DATASET_PATH = "data/financial_dataset.json"

new_examples = [

    # 1. Financial calculations

    {
        "instruction": "A person deposits Rs. 10,000 at a simple interest rate of 5% per year for 3 years. Calculate the interest and total amount.",
        "response": "Simple Interest = (Principal × Rate × Time) / 100. Here, Principal = Rs. 10,000, Rate = 5%, and Time = 3 years. Interest = (10,000 × 5 × 3) / 100 = Rs. 1,500. Total Amount = Principal + Interest = Rs. 11,500."
    },

    {
        "instruction": "A person invests Rs. 5,000 at 10% annual compound interest for 2 years. Calculate the final amount.",
        "response": "The compound interest formula is A = P(1 + r/100)^t. Here, P = Rs. 5,000, r = 10%, and t = 2. A = 5,000 × (1.10)^2 = Rs. 6,050. The compound interest earned is Rs. 1,050."
    },

    {
        "instruction": "A product costs Rs. 2,000 and its price increases by 10%. What is the new price?",
        "response": "The price increase is 10% of Rs. 2,000, which is Rs. 200. New price = Rs. 2,000 + Rs. 200 = Rs. 2,200."
    },

    {
        "instruction": "A person earns Rs. 40,000 per month and saves Rs. 8,000. Calculate the savings rate.",
        "response": "Savings Rate = (Monthly Savings / Monthly Income) × 100. Savings Rate = (8,000 / 40,000) × 100 = 20%. The person saves 20% of their monthly income."
    },

    {
        "instruction": "A loan of Rs. 50,000 has an annual simple interest rate of 12%. Calculate the interest for 6 months.",
        "response": "Simple Interest = (Principal × Rate × Time) / 100. Six months equals 0.5 years. Interest = (50,000 × 12 × 0.5) / 100 = Rs. 3,000. This calculation assumes simple interest and excludes fees or other charges."
    },

    # 2. Financial comparisons

    {
        "instruction": "What is the difference between a savings account and a fixed deposit?",
        "response": "A savings account allows deposits and withdrawals while generally earning interest on the account balance. A fixed deposit keeps money invested for a selected period and generally offers a predetermined interest rate. Savings accounts provide greater access to money, while fixed deposits may offer higher interest in exchange for reduced flexibility. Actual rates and withdrawal conditions depend on the bank."
    },

    {
        "instruction": "Explain the difference between simple interest and compound interest with an example.",
        "response": "Simple interest is calculated only on the original principal. Compound interest is calculated on the principal and previously accumulated interest. For example, Rs. 1,000 at 10% annually for two years earns Rs. 200 under simple interest, resulting in Rs. 1,200. Under annual compounding, the amount becomes Rs. 1,210 because the second year's interest is calculated on Rs. 1,100."
    },

    {
        "instruction": "What is the difference between a stock and a bond?",
        "response": "A stock represents partial ownership in a company. A shareholder may benefit from increases in share price and dividends, but can also lose money. A bond represents money lent to an issuer, which may be a company or government. The issuer generally promises interest payments and repayment of principal according to the bond terms. Stocks and bonds have different risks and returns."
    },

    {
        "instruction": "Compare an index fund and an actively managed mutual fund.",
        "response": "An index fund attempts to track a particular market index by holding investments that follow its composition. An actively managed mutual fund has a fund manager who selects investments with the goal of achieving a particular objective. Index funds often have lower management costs, while actively managed funds may have higher expenses. Neither approach guarantees positive returns or outperformance."
    },

    {
        "instruction": "What is the difference between a debit card and a credit card?",
        "response": "A debit card generally deducts money directly from the linked bank account when a transaction is completed. A credit card allows the cardholder to borrow money from the card issuer up to an approved credit limit. Credit card balances must be repaid according to billing terms, and unpaid balances may attract interest and fees. Debit cards use available bank funds, while credit cards involve borrowing."
    },

    # 3. Real-world financial scenarios

    {
        "instruction": "A person spends almost their entire monthly salary and has no emergency savings. What financial steps could help?",
        "response": "The person can begin by tracking monthly income and expenses, separating essential expenses from discretionary spending, and identifying costs that can be reduced. They can create a realistic monthly budget and start saving a small fixed amount regularly. Over time, they can build an emergency fund for unexpected expenses. The savings target should reflect their income, obligations, and personal circumstances."
    },

    {
        "instruction": "A person has multiple loans with different interest rates. How can they organize their repayment?",
        "response": "They should list each loan's outstanding balance, interest rate, minimum payment, and due date. They should continue making required minimum payments and examine whether extra payments can be directed toward the highest-interest loan first. This is commonly called the debt avalanche method. Another approach is the debt snowball method, which prioritizes the smallest balance. The suitable approach depends on the person's financial situation and motivation."
    },

    {
        "instruction": "A person wants to purchase an expensive phone using a credit card EMI. What should they consider before purchasing?",
        "response": "They should examine the total repayment amount, interest rate, processing fees, taxes, repayment period, and any conditions attached to a no-cost EMI offer. They should also consider their existing obligations and whether the monthly payment fits their budget. A lower monthly payment does not necessarily mean a lower total cost."
    },

    {
        "instruction": "A person receives an unexpected medical bill and does not have enough savings. What financial options might they examine?",
        "response": "They can first review available health insurance coverage, hospital payment arrangements, and any applicable reimbursement options. They may also examine available savings or assistance from reliable support sources. If borrowing is necessary, they should compare the total repayment cost and terms before accepting a loan. They should avoid making rushed decisions based on unclear lending offers."
    },

    {
        "instruction": "A person notices that their bank account balance is decreasing every month despite receiving a regular salary. What should they investigate?",
        "response": "They should compare monthly income with spending and examine recurring payments, subscriptions, loan EMIs, bank charges, and discretionary purchases. Reviewing bank statements and categorizing expenses can help identify where money is going. They can then create a budget and monitor spending regularly."
    },

    # 4. Risk and investment concepts

    {
        "instruction": "Why is diversification important in investing?",
        "response": "Diversification means spreading investments across different assets, industries, or investment categories instead of concentrating money in one place. It can reduce the effect of poor performance from a single investment on the overall portfolio. However, diversification cannot eliminate all investment risk or guarantee a profit."
    },

    {
        "instruction": "What is the relationship between risk and return in investing?",
        "response": "Risk refers to the possibility that an investment's actual return may differ from the expected return, including the possibility of losing money. Higher expected returns are often associated with higher risk, but taking more risk does not guarantee higher returns. Investors should understand the risks and time horizon of an investment before making decisions."
    },

    {
        "instruction": "What is liquidity risk?",
        "response": "Liquidity risk is the possibility that an asset cannot be converted into cash quickly without accepting a significant reduction in its price. For example, an asset with very few buyers may take a long time to sell. Liquidity is important because investors may need access to money when unexpected expenses occur."
    },

    {
        "instruction": "What happens when inflation increases while savings earn a lower interest rate?",
        "response": "When inflation is higher than the interest earned on savings, the purchasing power of the saved money decreases over time. For example, if savings earn 3% annually while prices increase by 6%, the savings balance grows in nominal terms but its purchasing power declines. Taxes and compounding can also affect the actual return."
    },

    {
        "instruction": "Can an investment that provides high returns also have high risk?",
        "response": "Yes. Investments with the possibility of high returns may also involve significant uncertainty and the possibility of large losses. However, high risk does not guarantee high returns. It is important to examine the investment's characteristics, costs, liquidity, and potential downside rather than judging it only by its expected return."
    },

    # 5. Financial literacy and responsible guidance

    {
        "instruction": "What information should a person review before taking a personal loan?",
        "response": "A person should review the loan amount, annual interest rate, repayment period, EMI, processing fees, late payment charges, prepayment conditions, and total repayment amount. They should also consider their income, existing debt, and ability to make payments on time. Comparing the complete loan terms is more useful than comparing interest rates alone."
    },

    {
        "instruction": "Why is paying only the minimum amount due on a credit card potentially expensive?",
        "response": "Paying only the minimum amount due may prevent the account from becoming overdue, depending on the card terms, but the remaining balance can continue to attract interest. This can increase the total repayment cost and extend the time required to clear the debt. Paying the full statement balance by the due date generally helps avoid interest on eligible purchases, subject to the card agreement."
    },

    {
        "instruction": "What is net worth and how is it calculated?",
        "response": "Net worth is the difference between a person's total assets and total liabilities. Assets may include cash, savings, investments, and property. Liabilities may include loans, credit card balances, and other debts. Net Worth = Total Assets - Total Liabilities."
    },

    {
        "instruction": "What is the difference between an asset and a liability?",
        "response": "An asset is something a person or organization owns or controls that has economic value, such as cash, investments, or property. A liability is an obligation that must be paid or settled, such as a loan, unpaid bill, or credit card balance."
    },

    {
        "instruction": "What is an expense ratio in a mutual fund?",
        "response": "An expense ratio represents the annual operating expenses of a mutual fund as a percentage of its assets. These expenses reduce the fund's returns to investors. When comparing funds, investors can examine expense ratios along with investment strategy, risk, tracking performance, and other costs."
    },

    {
        "instruction": "What should a person do if they receive a suspicious message asking for their banking password or OTP?",
        "response": "They should not share their banking password, PIN, or one-time password. They should avoid clicking suspicious links and should contact their bank through its official website, application, or verified customer support number. If banking details have already been shared, they should immediately contact the bank and follow its security instructions."
    },

    {
        "instruction": "Can a financial AI assistant guarantee that an investment will make a profit?",
        "response": "No. A financial AI assistant cannot guarantee investment profits or predict market outcomes with certainty. Investment values can change due to market conditions, economic events, and other factors. AI-generated information may also be incomplete or incorrect. Users should independently verify financial information and consult a qualified financial professional when appropriate."
    },

    {
        "instruction": "A user asks an AI assistant which stock they should buy to double their money in one month. How should the assistant respond?",
        "response": "The assistant should explain that no stock can be reliably guaranteed to double in one month and that attempting to achieve such a return involves substantial risk. It should not present a specific stock as a guaranteed opportunity. It can instead explain investment risk, diversification, time horizon, and the importance of independent research and qualified financial guidance."
    },

    {
        "instruction": "Why should financial information generated by an AI model be verified?",
        "response": "AI models can produce incorrect, outdated, or misleading financial information. Financial rules, product terms, interest rates, and market conditions may change. Users should verify important information using reliable and current sources, such as official bank documents, regulators, and financial institutions."
    }

]


# Load existing dataset
if os.path.exists(DATASET_PATH):

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        dataset = json.load(file)

else:
    dataset = []


# Find existing instructions
existing_questions = {
    item["instruction"].strip().lower()
    for item in dataset
}


# Add only unique examples
added = 0

for example in new_examples:

    question = example["instruction"].strip().lower()

    if question not in existing_questions:

        dataset.append(example)
        existing_questions.add(question)
        added += 1


# Save updated dataset
with open(DATASET_PATH, "w", encoding="utf-8") as file:

    json.dump(
        dataset,
        file,
        indent=4,
        ensure_ascii=False
    )


print("Advanced dataset expansion completed!")
print("New examples added:", added)
print("Total examples:", len(dataset))