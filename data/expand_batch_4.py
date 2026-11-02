import json
import os

DATASET_PATH = "data/financial_dataset.json"

new_examples = [

    # SECTION 1: FINANCIAL STATEMENTS (1–10)

    {
        "instruction": "What is an income statement?",
        "response": "An income statement is a financial report showing a company's revenue, expenses, and profit or loss over a particular period. It helps users understand how the company performed financially. Revenue minus expenses gives the resulting profit or loss."
    },
    {
        "instruction": "What is a balance sheet?",
        "response": "A balance sheet is a financial statement showing a company's assets, liabilities, and shareholders' equity at a specific point in time. It follows the accounting equation: Assets = Liabilities + Equity. It provides information about the company's financial position."
    },
    {
        "instruction": "What is a cash flow statement?",
        "response": "A cash flow statement reports the cash entering and leaving a business during a period. It classifies cash flows into operating, investing, and financing activities. It helps users understand how a business generates and uses cash."
    },
    {
        "instruction": "What is gross profit?",
        "response": "Gross profit is the amount remaining after subtracting the cost of goods sold from revenue. Formula: Gross Profit = Revenue - Cost of Goods Sold. It indicates how much a company earns from its products or services before operating expenses and other costs."
    },
    {
        "instruction": "A company earns Rs. 5,00,000 in revenue and has a cost of goods sold of Rs. 3,00,000. Calculate gross profit.",
        "response": "Gross Profit = Revenue - Cost of Goods Sold. Gross Profit = Rs. 5,00,000 - Rs. 3,00,000 = Rs. 2,00,000."
    },
    {
        "instruction": "What is operating profit?",
        "response": "Operating profit is the profit generated from a company's normal business operations after deducting operating expenses from gross profit. It generally excludes interest expenses and income taxes. It helps evaluate the profitability of the company's core operations."
    },
    {
        "instruction": "A business has revenue of Rs. 8,00,000 and total expenses of Rs. 6,50,000. Calculate its profit.",
        "response": "Profit = Revenue - Total Expenses. Profit = Rs. 8,00,000 - Rs. 6,50,000 = Rs. 1,50,000. This assumes all relevant expenses are included in the stated amount."
    },
    {
        "instruction": "What is the difference between revenue and profit?",
        "response": "Revenue is the total income generated from selling goods or providing services before deducting expenses. Profit is the amount remaining after relevant expenses are deducted from revenue. A company can generate high revenue but still report a low profit or a loss."
    },
    {
        "instruction": "What is working capital?",
        "response": "Working capital measures the difference between current assets and current liabilities. Formula: Working Capital = Current Assets - Current Liabilities. It provides an indication of a company's ability to meet short-term financial obligations."
    },
    {
        "instruction": "A business has current assets of Rs. 4,00,000 and current liabilities of Rs. 2,50,000. Calculate working capital.",
        "response": "Working Capital = Current Assets - Current Liabilities. Working Capital = Rs. 4,00,000 - Rs. 2,50,000 = Rs. 1,50,000."
    },

    # SECTION 2: INSURANCE AND RISK MANAGEMENT (11–20)

    {
        "instruction": "What is insurance?",
        "response": "Insurance is a financial arrangement in which an insurer provides specified financial protection against covered risks in exchange for a premium. Coverage depends on the policy terms, exclusions, limits, and conditions. Insurance can help reduce the financial impact of unexpected events."
    },
    {
        "instruction": "What is an insurance premium?",
        "response": "An insurance premium is the amount a policyholder pays to maintain insurance coverage. It may be paid monthly, quarterly, annually, or according to the policy terms. Premium amounts depend on factors such as coverage, risk, age, and the type of insurance."
    },
    {
        "instruction": "What is a deductible in insurance?",
        "response": "A deductible is the amount a policyholder must pay toward a covered claim before the insurer pays its eligible share, subject to the policy terms. A higher deductible may reduce the premium in some policies, but it can increase the policyholder's out-of-pocket expense during a claim."
    },
    {
        "instruction": "What is the difference between life insurance and health insurance?",
        "response": "Life insurance provides a specified financial benefit to beneficiaries or other eligible recipients when the insured person dies, subject to policy conditions. Health insurance helps cover eligible medical expenses according to its terms. The two products address different financial risks."
    },
    {
        "instruction": "What is term life insurance?",
        "response": "Term life insurance provides life coverage for a specified period. If the insured person dies during the policy term, the insurer pays the eligible death benefit according to the policy conditions. Traditional term insurance generally focuses on protection rather than investment returns."
    },
    {
        "instruction": "What is an insurance claim?",
        "response": "An insurance claim is a formal request made by a policyholder or eligible beneficiary asking the insurer to provide a benefit or payment for a covered event. The insurer reviews the submitted information and supporting documents before deciding whether the claim is payable under the policy."
    },
    {
        "instruction": "What is underinsurance?",
        "response": "Underinsurance occurs when the coverage amount is insufficient to meet the financial loss caused by an insured event. For example, property insured for much less than its replacement value may leave the owner responsible for a large portion of the loss."
    },
    {
        "instruction": "Why should someone read insurance policy exclusions?",
        "response": "Policy exclusions describe situations, conditions, or expenses that are not covered by the insurance policy. Understanding them helps policyholders avoid incorrect assumptions about coverage. They should also review waiting periods, coverage limits, deductibles, and claim conditions."
    },
    {
        "instruction": "What is an emergency fund and how is it different from insurance?",
        "response": "An emergency fund is money set aside for unexpected expenses and is generally accessible when needed. Insurance transfers specified financial risks to an insurer in exchange for premiums. An emergency fund provides immediate financial flexibility, while insurance offers protection against covered events. They serve different purposes."
    },
    {
        "instruction": "A person has health insurance but their medical expense is excluded by the policy. What should they understand?",
        "response": "Insurance coverage depends on the policy's specific terms and exclusions. Having health insurance does not mean every medical expense will automatically be covered. The person should review the policy document, obtain the insurer's explanation, and follow the official grievance or appeal process if they believe the decision is incorrect."
    },

    # SECTION 3: TAX AND FINANCIAL PLANNING CONCEPTS (21–30)

    {
        "instruction": "What is income tax?",
        "response": "Income tax is a tax imposed by a government on taxable income earned by individuals or organizations. The amount payable depends on applicable tax laws, income categories, deductions, exemptions, and tax rates. Tax rules differ across countries and may change over time."
    },
    {
        "instruction": "What is taxable income?",
        "response": "Taxable income is the portion of income on which tax is calculated after applying the deductions, exemptions, adjustments, and rules permitted under the relevant tax system. It may differ from a person's total or gross income."
    },
    {
        "instruction": "What is the difference between gross income and net income?",
        "response": "Gross income is income before certain deductions and adjustments. Net income is the amount remaining after applicable deductions or expenses, depending on the context. In a salary context, take-home pay is generally the amount received after payroll deductions."
    },
    {
        "instruction": "What is a progressive tax system?",
        "response": "A progressive tax system generally applies higher marginal tax rates to higher levels of taxable income. This means that different portions of taxable income may be taxed at different rates. The exact tax brackets and rules depend on the jurisdiction."
    },
    {
        "instruction": "What is a tax deduction?",
        "response": "A tax deduction is an amount that eligible taxpayers may subtract from income when calculating taxable income, according to applicable tax rules. Deductions can reduce taxable income, but eligibility, limits, and documentation requirements depend on the tax jurisdiction."
    },
    {
        "instruction": "What is a tax credit?",
        "response": "A tax credit is an amount that can reduce the tax payable directly, subject to the applicable rules. Unlike a deduction, which generally reduces taxable income, a tax credit reduces the calculated tax liability. Eligibility and refundability vary by jurisdiction."
    },
    {
        "instruction": "What is tax planning?",
        "response": "Tax planning involves organizing financial activities within the law to understand and manage tax obligations. It may include reviewing eligible deductions, exemptions, investment-related tax rules, and payment deadlines. Tax planning should use current official regulations and should not involve hiding income or submitting false information."
    },
    {
        "instruction": "What is the difference between tax avoidance and tax evasion?",
        "response": "Tax avoidance generally refers to arranging financial activities to reduce tax legally using permitted provisions. Tax evasion involves illegally concealing income, falsifying records, or deliberately avoiding tax obligations. Tax evasion can result in penalties and legal consequences."
    },
    {
        "instruction": "Why should financial tax information be checked against current government rules?",
        "response": "Tax laws, rates, deadlines, deductions, and reporting requirements can change. Financial information from older sources may no longer be accurate. Important tax decisions should be verified using current official government publications or qualified tax professionals."
    },
    {
        "instruction": "What information should a person organize before preparing an annual tax return?",
        "response": "They should organize income statements, salary records, bank interest details, investment records, eligible deduction documents, tax payment records, and other relevant supporting documents. The exact documents depend on their jurisdiction and income sources. They should check the current official filing requirements."
    },

    # SECTION 4: FINANCIAL GOALS AND LONG-TERM PLANNING (31–40)

    {
        "instruction": "What is retirement planning?",
        "response": "Retirement planning is the process of preparing financially for the period when a person reduces or stops regular employment. It involves estimating future expenses, considering inflation, evaluating retirement income sources, and building savings over time. The plan should be reviewed as circumstances change."
    },
    {
        "instruction": "Why is inflation important when planning for retirement?",
        "response": "Inflation reduces the purchasing power of money over time. Expenses that seem affordable today may become significantly higher in the future. Retirement planning should therefore consider the expected increase in living costs rather than relying only on today's expenses."
    },
    {
        "instruction": "What is the time value of money?",
        "response": "The time value of money is the principle that money available today can be worth more than the same amount received in the future because it can potentially earn returns. Inflation, risk, and the opportunity to invest are important reasons behind this concept."
    },
    {
        "instruction": "What is a financial goal?",
        "response": "A financial goal is a specific objective that a person plans to achieve using money. Examples include building emergency savings, paying education expenses, purchasing a home, or preparing for retirement. A useful goal includes a target amount and an expected time frame."
    },
    {
        "instruction": "What is the difference between a short-term and a long-term financial goal?",
        "response": "A short-term financial goal is generally intended to be achieved within a relatively short period, such as saving for an annual expense. A long-term financial goal may require many years, such as retirement planning or funding higher education. Their time horizons can influence suitable saving and investment approaches."
    },
    {
        "instruction": "A person wants to save Rs. 1,20,000 in 12 months. How much should they save each month if there is no interest?",
        "response": "Monthly Savings = Target Amount / Number of Months. Monthly Savings = Rs. 1,20,000 / 12 = Rs. 10,000. The person needs to save Rs. 10,000 every month, assuming no interest or additional fees."
    },
    {
        "instruction": "Why should financial goals have a specific target amount and deadline?",
        "response": "A target amount and deadline make a financial goal measurable. They help a person estimate how much needs to be saved regularly, monitor progress, and adjust the plan when necessary. Without a target and time frame, it is harder to measure whether the goal is being achieved."
    },
    {
        "instruction": "What is a retirement corpus?",
        "response": "A retirement corpus is the accumulated pool of savings and investments intended to support expenses after retirement. Its required size depends on expected living costs, inflation, retirement duration, income sources, and investment returns. Estimates are uncertain and should be reviewed periodically."
    },
    {
        "instruction": "Why should someone review their financial plan regularly?",
        "response": "Income, expenses, family responsibilities, financial goals, market conditions, and personal circumstances can change over time. Reviewing a financial plan helps identify whether savings, insurance, debt repayment, and investment arrangements remain appropriate. A review also helps identify gaps and adjust targets."
    },
    {
        "instruction": "A person receives a salary increase. What financial areas could they review before increasing spending?",
        "response": "They could review emergency savings, outstanding high-cost debt, insurance coverage, retirement contributions, upcoming financial goals, and monthly expenses. Allocating part of an income increase toward savings or debt repayment may help strengthen financial stability instead of allowing all additional income to become new spending."
    },

    # SECTION 5: MULTI-STEP FINANCIAL SCENARIOS AND CALCULATIONS (41–50)

    {
        "instruction": "A person earns Rs. 60,000 monthly. Their rent is Rs. 15,000, groceries cost Rs. 8,000, transport costs Rs. 4,000, and utilities cost Rs. 3,000. Calculate the remaining amount.",
        "response": "Total Expenses = 15,000 + 8,000 + 4,000 + 3,000 = Rs. 30,000. Remaining Amount = Income - Expenses = Rs. 60,000 - Rs. 30,000 = Rs. 30,000. This is the amount remaining before any other expenses or savings allocations."
    },
    {
        "instruction": "A person has Rs. 50,000 in savings. They spend Rs. 12,000 on rent, Rs. 5,000 on groceries, and Rs. 3,000 on transport. Calculate their remaining savings.",
        "response": "Total Spending = Rs. 12,000 + Rs. 5,000 + Rs. 3,000 = Rs. 20,000. Remaining Savings = Rs. 50,000 - Rs. 20,000 = Rs. 30,000."
    },
    {
        "instruction": "A product costs Rs. 10,000. A shop offers a 10% discount followed by an additional 5% discount on the reduced price. Calculate the final price.",
        "response": "First Discount = 10% of Rs. 10,000 = Rs. 1,000. Price After First Discount = Rs. 9,000. Second Discount = 5% of Rs. 9,000 = Rs. 450. Final Price = Rs. 9,000 - Rs. 450 = Rs. 8,550. The discounts are applied successively, not added together."
    },
    {
        "instruction": "A person invests Rs. 20,000 and receives Rs. 2,000 in dividends. The investment's market value increases to Rs. 22,000. Calculate the total gain and return, ignoring costs and taxes.",
        "response": "Capital Gain = Rs. 22,000 - Rs. 20,000 = Rs. 2,000. Dividend Income = Rs. 2,000. Total Gain = Rs. 2,000 + Rs. 2,000 = Rs. 4,000. Total Return = (4,000 / 20,000) × 100 = 20%. This calculation assumes the dividend is received and excludes costs and taxes."
    },
    {
        "instruction": "A person's monthly income is Rs. 70,000. They spend Rs. 42,000 and repay Rs. 8,000 in debt. Calculate the amount remaining.",
        "response": "Total Allocations = Expenses + Debt Repayment = Rs. 42,000 + Rs. 8,000 = Rs. 50,000. Remaining Amount = Rs. 70,000 - Rs. 50,000 = Rs. 20,000. This amount can be considered for savings or other financial goals."
    },
    {
        "instruction": "An investor purchases 20 units of a fund at Rs. 100 per unit and another 30 units at Rs. 120 per unit. Calculate the average purchase cost per unit.",
        "response": "First Purchase Cost = 20 × Rs. 100 = Rs. 2,000. Second Purchase Cost = 30 × Rs. 120 = Rs. 3,600. Total Cost = Rs. 5,600. Total Units = 20 + 30 = 50. Average Purchase Cost = Rs. 5,600 / 50 = Rs. 112 per unit."
    },
    {
        "instruction": "A person has an emergency fund of Rs. 90,000 and monthly essential expenses of Rs. 30,000. How many months of essential expenses can the fund cover?",
        "response": "Emergency Fund Coverage = Emergency Savings / Monthly Essential Expenses. Coverage = Rs. 90,000 / Rs. 30,000 = 3 months. This assumes the monthly essential expenses remain unchanged."
    },
    {
        "instruction": "A company reports revenue of Rs. 10,00,000, operating expenses of Rs. 3,00,000, and cost of goods sold of Rs. 4,00,000. Calculate operating profit using these figures.",
        "response": "Gross Profit = Revenue - Cost of Goods Sold = Rs. 10,00,000 - Rs. 4,00,000 = Rs. 6,00,000. Operating Profit = Gross Profit - Operating Expenses = Rs. 6,00,000 - Rs. 3,00,000 = Rs. 3,00,000. This assumes the listed operating expenses are complete."
    },
    {
        "instruction": "A borrower owes Rs. 2,00,000. They repay Rs. 25,000 toward principal and are charged Rs. 2,000 in interest. Calculate the total payment and remaining principal.",
        "response": "Total Payment = Principal Repayment + Interest = Rs. 25,000 + Rs. 2,000 = Rs. 27,000. Remaining Principal = Rs. 2,00,000 - Rs. 25,000 = Rs. 1,75,000. The interest payment does not reduce the principal."
    },
    {
        "instruction": "A person saves Rs. 6,000 per month for 6 months and then withdraws Rs. 8,000. Calculate the remaining savings, excluding interest.",
        "response": "Total Deposits = Rs. 6,000 × 6 = Rs. 36,000. Remaining Savings = Rs. 36,000 - Rs. 8,000 = Rs. 28,000. This excludes interest, fees, and any other transactions."
    },

    # SECTION 6: FINANCIAL AI SAFETY AND REASONING (51–60)

    {
        "instruction": "A user asks a financial AI assistant to provide a guaranteed investment return. How should it respond?",
        "response": "The assistant should explain that investment returns cannot be guaranteed for market-linked products. It should not promise a specific profit or present uncertain projections as certain outcomes. It can explain the risks, factors affecting returns, and the importance of reviewing reliable information before making financial decisions."
    },
    {
        "instruction": "A user provides a bank password and asks a financial chatbot to log into their account. What should the chatbot do?",
        "response": "The chatbot should not request, store, or use the user's banking password. It should warn the user not to share credentials and direct them to access their bank through its official secure application or website. Sensitive authentication information must be protected."
    },
    {
        "instruction": "A financial chatbot receives a question about a tax rule that may have changed recently. What should it do?",
        "response": "The chatbot should disclose that its information may not reflect the latest tax rules. It should avoid presenting uncertain information as current law and direct the user to official government tax publications or a qualified tax professional. If a verified current-data source is available, it should use that source and identify its date."
    },
    {
        "instruction": "A user asks an AI assistant to create fake income documents for a loan application. How should it respond?",
        "response": "The assistant should refuse to help create or falsify financial documents. It can explain that submitting false information may lead to legal and financial consequences. It can suggest preparing accurate income records and contacting the lender about legitimate documentation requirements."
    },
    {
        "instruction": "A financial AI assistant gives a calculation result without explaining its assumptions. Why is this a problem?",
        "response": "A financial calculation depends on assumptions such as interest rate, compounding frequency, time period, fees, and payment timing. Without explaining these assumptions, the result may be misunderstood or applied incorrectly. The assistant should show its formula, inputs, calculation, and relevant limitations."
    },
    {
        "instruction": "A user asks an AI assistant to choose between two investments but provides no information about their financial goals or risk tolerance. How should the assistant respond?",
        "response": "The assistant should avoid making an unsupported personalized recommendation. It can explain general differences between the investments, including risks, liquidity, costs, and possible return characteristics. It should clarify that suitability depends on personal circumstances and encourage independent verification or qualified financial guidance."
    },
    {
        "instruction": "What should a financial AI assistant do when it does not know the answer to a question?",
        "response": "The assistant should clearly acknowledge uncertainty rather than inventing an answer. It can explain what information is missing, suggest reliable sources for verification, or ask a relevant clarifying question. Avoiding unsupported financial claims is important for user safety."
    },
    {
        "instruction": "Why should a financial AI application keep logs of model errors and user feedback?",
        "response": "Logging model errors and user feedback helps developers identify recurring problems, measure application reliability, and improve responses. Logs should be designed to protect sensitive personal and financial information. Access controls, data minimization, retention limits, and appropriate security measures should be applied."
    },
    {
        "instruction": "A financial chatbot receives a question containing private account numbers. How should the application handle the information?",
        "response": "The application should avoid collecting unnecessary account information and should protect sensitive data using appropriate security controls. Sensitive values should be masked or excluded from logs where possible. Access should be restricted, and data should only be processed for legitimate purposes with suitable safeguards."
    },
    {
        "instruction": "How can developers evaluate whether a financial AI assistant produces reliable answers?",
        "response": "Developers can create a held-out evaluation dataset containing financial definitions, calculations, comparisons, and safety scenarios. They can measure response accuracy, calculation correctness, relevance, instruction following, and hallucination rates. Human review by knowledgeable evaluators is important because language-model loss alone cannot establish financial correctness."
    }

]


# Verify exact batch size before saving
if len(new_examples) != 60:
    raise ValueError(
        f"Expected 60 examples, but found {len(new_examples)}."
    )


# Load existing dataset
if os.path.exists(DATASET_PATH):
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        dataset = json.load(file)
else:
    dataset = []


# Identify existing questions
existing_questions = {
    item["instruction"].strip().lower()
    for item in dataset
}


# Add unique examples
added = 0
duplicates = 0

for example in new_examples:

    question = example["instruction"].strip().lower()

    if question not in existing_questions:
        dataset.append(example)
        existing_questions.add(question)
        added += 1
    else:
        duplicates += 1


# Save updated dataset
with open(DATASET_PATH, "w", encoding="utf-8") as file:
    json.dump(
        dataset,
        file,
        indent=4,
        ensure_ascii=False
    )


print("Batch 4 expansion completed!")
print("Examples in this batch:", len(new_examples))
print("New examples added:", added)
print("Duplicates skipped:", duplicates)
print("Total dataset examples:", len(dataset))