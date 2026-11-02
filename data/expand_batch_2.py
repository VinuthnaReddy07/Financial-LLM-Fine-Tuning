import json
import os

DATASET_PATH = "data/financial_dataset.json"

new_examples = [

    # BANKING AND SAVINGS (1–12)

    {
        "instruction": "What is the difference between a current account and a savings account?",
        "response": "A savings account is generally designed for individuals to save money and earn interest while accessing their funds. A current account is commonly used by businesses for frequent transactions. Current accounts may provide features such as higher transaction limits, depending on the bank. Interest rates, fees, and account conditions vary by institution."
    },
    {
        "instruction": "What is a minimum balance requirement in a bank account?",
        "response": "A minimum balance requirement is the amount a bank may require a customer to maintain in an account. If the balance falls below the required amount, the bank may charge a penalty depending on the account terms. Some accounts have no minimum balance requirement."
    },
    {
        "instruction": "What is a recurring deposit?",
        "response": "A recurring deposit is a savings product in which a person deposits a fixed amount at regular intervals, usually monthly, for a selected period. The deposited amount earns interest according to the bank's terms. It encourages regular saving, and the maturity amount depends on the deposit amount, duration, and applicable interest rate."
    },
    {
        "instruction": "How is a recurring deposit different from a fixed deposit?",
        "response": "A recurring deposit allows a person to deposit a fixed amount regularly, often every month. A fixed deposit generally involves depositing a lump sum for a selected period. Both may earn interest, but their deposit schedules and maturity calculations differ."
    },
    {
        "instruction": "What is a bank statement and why should customers review it?",
        "response": "A bank statement is a record of transactions in a bank account over a particular period. It normally includes deposits, withdrawals, transfers, charges, and account balances. Reviewing it helps customers track spending, identify unauthorized transactions, and check whether expected payments have been processed."
    },
    {
        "instruction": "What is an overdraft facility?",
        "response": "An overdraft facility allows an eligible bank customer to withdraw or spend more money than the available account balance, up to an approved limit. The borrowed amount may attract interest and fees. The customer should review the repayment conditions and charges before using the facility."
    },
    {
        "instruction": "What is the difference between NEFT, RTGS, and IMPS?",
        "response": "NEFT, RTGS, and IMPS are electronic fund transfer systems used in India. NEFT processes transfers in batches at frequent intervals. RTGS is designed for real-time settlement of eligible high-value transfers. IMPS supports immediate fund transfers. Customers should check their bank's current limits, charges, and availability."
    },
    {
        "instruction": "What is a UPI transaction?",
        "response": "Unified Payments Interface, or UPI, is an Indian digital payment system that allows users to transfer money between participating bank accounts using a mobile application. Payments can be made using identifiers such as a UPI ID or QR code. Users should verify the recipient and never share their UPI PIN."
    },
    {
        "instruction": "A customer sees an unfamiliar debit in their bank statement. What should they do?",
        "response": "The customer should verify the transaction details and check whether it relates to a known payment or subscription. If it remains unfamiliar, they should promptly contact their bank through official channels, report the transaction, and follow the bank's instructions. They should secure their account and avoid sharing passwords, PINs, or OTPs."
    },
    {
        "instruction": "What is a dormant bank account?",
        "response": "A dormant bank account is an account that has had no customer-initiated transactions for a period specified by the bank or applicable regulations. The account may have restrictions until the customer completes the required reactivation process. The exact rules depend on the bank and jurisdiction."
    },
    {
        "instruction": "What is the difference between a nominal interest rate and an effective interest rate?",
        "response": "The nominal interest rate is the stated annual interest rate before considering the effect of compounding. The effective annual interest rate includes the effect of compounding during the year. When interest is compounded more frequently, the effective rate can be higher than the nominal rate."
    },
    {
        "instruction": "A person deposits Rs. 20,000 in an account earning 5% simple annual interest for two years. Calculate the maturity amount.",
        "response": "Simple Interest = Principal × Rate × Time / 100. Interest = 20,000 × 5 × 2 / 100 = Rs. 2,000. Maturity Amount = Principal + Interest = Rs. 22,000. This calculation assumes no additional deposits, withdrawals, or fees."
    },

    # LOANS AND REPAYMENT (13–26)

    {
        "instruction": "What is an EMI?",
        "response": "EMI stands for Equated Monthly Instalment. It is the regular monthly payment made by a borrower toward repaying a loan. An EMI generally includes both principal repayment and interest. Its amount depends on the loan principal, interest rate, and repayment tenure."
    },
    {
        "instruction": "What happens when a borrower misses a loan EMI?",
        "response": "Missing a loan EMI may result in late payment charges, additional interest, and a negative effect on the borrower's credit history, depending on the lender's policies and applicable reporting rules. Repeated missed payments can create more serious repayment problems. The borrower should contact the lender promptly to understand available options."
    },
    {
        "instruction": "What is loan tenure?",
        "response": "Loan tenure is the period agreed upon for repaying a loan. A longer tenure generally reduces the monthly EMI but may increase the total interest paid. A shorter tenure generally increases the EMI but can reduce the overall interest cost."
    },
    {
        "instruction": "What is the principal amount of a loan?",
        "response": "The principal is the original amount borrowed from a lender, excluding interest and other charges. As repayments are made, part of each payment may reduce the outstanding principal while another part pays interest."
    },
    {
        "instruction": "What is a secured loan?",
        "response": "A secured loan is a loan backed by an asset provided as collateral. Examples may include certain home loans and vehicle loans. If the borrower fails to meet repayment obligations, the lender may have rights over the collateral according to the loan agreement and applicable law."
    },
    {
        "instruction": "What is an unsecured loan?",
        "response": "An unsecured loan is not backed by a specific asset as collateral. Personal loans and some education loans may be unsecured. Lenders assess factors such as income, credit history, and repayment capacity. Interest rates may be higher than those of comparable secured loans."
    },
    {
        "instruction": "What is loan amortization?",
        "response": "Loan amortization is the process of repaying a loan through scheduled payments over time. Each payment generally covers interest and reduces the outstanding principal. In a typical fixed-payment loan, the interest portion decreases over time while the principal portion increases."
    },
    {
        "instruction": "How does a higher interest rate affect the EMI on a loan?",
        "response": "For the same loan amount and repayment tenure, a higher interest rate generally increases the EMI. It also increases the total interest paid over the loan period. The exact change depends on the loan's repayment structure and terms."
    },
    {
        "instruction": "A person borrows Rs. 1,00,000 at 10% simple annual interest for two years. Calculate the total repayment amount.",
        "response": "Simple Interest = Principal × Rate × Time / 100. Interest = 1,00,000 × 10 × 2 / 100 = Rs. 20,000. Total Repayment = Principal + Interest = Rs. 1,20,000. This is a simple-interest illustration, not an EMI calculation."
    },
    {
        "instruction": "A borrower has a loan balance of Rs. 80,000 and repays Rs. 10,000 toward principal. What is the remaining principal?",
        "response": "Remaining Principal = Original Outstanding Principal - Principal Repaid. Remaining Principal = Rs. 80,000 - Rs. 10,000 = Rs. 70,000. This assumes the Rs. 10,000 payment is applied entirely toward principal and excludes interest or fees."
    },
    {
        "instruction": "What is loan refinancing?",
        "response": "Loan refinancing means replacing an existing loan with a new loan, often to obtain different interest rates, repayment terms, or monthly payments. Before refinancing, borrowers should compare processing fees, foreclosure charges, total interest, and the new repayment schedule."
    },
    {
        "instruction": "What is loan foreclosure?",
        "response": "Loan foreclosure means repaying the outstanding loan amount in full before the scheduled end of the repayment period. Depending on the loan agreement and applicable regulations, the lender may apply specific charges or conditions. Borrowers should request an official outstanding balance and foreclosure statement."
    },
    {
        "instruction": "What is a debt-to-income ratio?",
        "response": "The debt-to-income ratio compares a person's recurring debt payments with their gross monthly income. It is commonly calculated as Total Monthly Debt Payments divided by Gross Monthly Income, multiplied by 100. Lenders may use it to assess repayment capacity. Different lenders may apply different thresholds."
    },
    {
        "instruction": "A person earns Rs. 60,000 monthly and pays Rs. 15,000 toward loan EMIs. Calculate the debt-to-income ratio using these figures.",
        "response": "Debt-to-Income Ratio = (Monthly Debt Payments / Gross Monthly Income) × 100. Here, the ratio is (15,000 / 60,000) × 100 = 25%. This calculation considers only the stated EMI amount and income."
    },

    # CREDIT AND CREDIT HISTORY (15 examples)

    {
        "instruction": "What is a credit report?",
        "response": "A credit report is a record of a person's credit accounts and repayment history. It may contain loan and credit card information, outstanding balances, payment history, and credit enquiries. Lenders may review it when assessing a credit application."
    },
    {
        "instruction": "What is the difference between a credit report and a credit score?",
        "response": "A credit report contains detailed information about a person's borrowing and repayment history. A credit score is a numerical summary calculated using information from a credit report and a scoring model. The score helps lenders assess credit risk, but lenders may consider additional information."
    },
    {
        "instruction": "Does checking your own credit score reduce it?",
        "response": "Checking your own credit score is generally treated as a soft enquiry and does not reduce the score. A lender's credit check during a credit application may be treated as a hard enquiry. The precise impact depends on the credit scoring system."
    },
    {
        "instruction": "What is credit utilization?",
        "response": "Credit utilization is the proportion of available revolving credit that a person is currently using. It is commonly calculated by dividing the outstanding credit card balance by the total credit limit and multiplying by 100. High utilization may negatively affect some credit scoring models."
    },
    {
        "instruction": "A credit card has a limit of Rs. 1,00,000 and an outstanding balance of Rs. 30,000. Calculate credit utilization.",
        "response": "Credit Utilization = (Outstanding Balance / Total Credit Limit) × 100. Credit Utilization = (30,000 / 1,00,000) × 100 = 30%."
    },
    {
        "instruction": "What is a hard enquiry on a credit report?",
        "response": "A hard enquiry may occur when a lender checks a person's credit report as part of evaluating a credit application. It can affect the credit score depending on the scoring model. Multiple applications within a short period may be viewed as a sign of increased borrowing activity."
    },
    {
        "instruction": "What is a soft enquiry on a credit report?",
        "response": "A soft enquiry is a credit report check that generally does not affect the credit score. It may occur when a person checks their own credit report or when an organization performs an eligible background credit check. Treatment depends on the credit reporting system."
    },
    {
        "instruction": "How can a person maintain a healthy credit history?",
        "response": "A person can maintain a healthy credit history by paying loan EMIs and credit card bills on time, monitoring credit reports, keeping borrowing manageable, and correcting inaccurate information. They should avoid applying for unnecessary credit and should review account statements regularly."
    },
    {
        "instruction": "What should someone do if their credit report contains an incorrect loan entry?",
        "response": "They should obtain the credit report, identify the incorrect entry, and raise a dispute with the relevant credit bureau and lender through official channels. They should keep supporting documents and track the dispute reference number. The correction process depends on verification by the reporting institution."
    },
    {
        "instruction": "Does having multiple credit cards automatically improve a credit score?",
        "response": "No. Having multiple credit cards does not automatically improve a credit score. Credit scoring can consider payment history, utilization, account age, enquiries, and other factors. Managing existing accounts responsibly is more important than opening additional accounts solely to increase a score."
    },
    {
        "instruction": "What is a credit limit?",
        "response": "A credit limit is the maximum amount a lender allows a customer to borrow or spend on a credit account. The limit is determined using factors such as income, credit history, and the lender's policies. Spending beyond the available limit may result in declined transactions or charges."
    },
    {
        "instruction": "What is a grace period on a credit card?",
        "response": "A grace period is the period between the end of a billing cycle and the payment due date during which eligible purchases may avoid interest if the full statement balance is paid on time. The conditions depend on the card agreement. Cash advances and certain transactions may not receive a grace period."
    },
    {
        "instruction": "Why is paying a credit card bill after the due date risky?",
        "response": "Late credit card payments may result in late fees, interest charges, and possible negative credit reporting. The impact depends on the card agreement and applicable reporting rules. Paying at least the required amount by the due date can help avoid some consequences, but paying the full statement balance may reduce interest costs."
    },
    {
        "instruction": "What is a credit card balance transfer?",
        "response": "A balance transfer moves outstanding debt from one credit card to another, often with the aim of obtaining a lower interest rate or promotional repayment period. Customers should compare transfer fees, promotional expiry dates, standard interest rates, and repayment conditions before proceeding."
    },
    {
        "instruction": "What is the difference between a prepaid card and a credit card?",
        "response": "A prepaid card is loaded with money in advance and spending is generally limited to the available balance. A credit card allows eligible purchases using borrowed funds up to an approved credit limit. A prepaid card does not normally involve borrowing, while a credit card creates a repayment obligation."
    },

    # BUDGETING AND CASH FLOW (12 examples)

    {
        "instruction": "What is a monthly budget?",
        "response": "A monthly budget is a plan for how a person expects to use their income during a month. It lists expected income and expenses, including essential costs, debt payments, savings, and discretionary spending. Comparing the budget with actual transactions helps identify spending patterns."
    },
    {
        "instruction": "What is the 50-30-20 budgeting rule?",
        "response": "The 50-30-20 rule is a budgeting guideline that allocates approximately 50% of after-tax income to needs, 30% to wants, and 20% to savings and debt repayment. It is a general framework rather than a strict requirement. Individuals may adjust the percentages based on their circumstances."
    },
    {
        "instruction": "A person earns Rs. 50,000 after tax. Using the 50-30-20 rule, calculate the suggested amounts for needs, wants, and savings.",
        "response": "Needs = 50% of Rs. 50,000 = Rs. 25,000. Wants = 30% of Rs. 50,000 = Rs. 15,000. Savings and debt repayment = 20% of Rs. 50,000 = Rs. 10,000. These are suggested allocations, not mandatory spending limits."
    },
    {
        "instruction": "What is cash flow in personal finance?",
        "response": "Personal cash flow is the movement of money into and out of a person's finances during a period. Income and other receipts are cash inflows, while rent, bills, loan payments, and purchases are cash outflows. Positive cash flow means inflows exceed outflows during the measured period."
    },
    {
        "instruction": "A person receives Rs. 45,000 monthly and spends Rs. 38,000. Calculate their monthly surplus.",
        "response": "Monthly Surplus = Monthly Income - Monthly Expenses. Monthly Surplus = Rs. 45,000 - Rs. 38,000 = Rs. 7,000. The person has Rs. 7,000 remaining before considering any additional unrecorded expenses."
    },
    {
        "instruction": "What is a sinking fund in budgeting?",
        "response": "A sinking fund is money saved gradually for a known future expense. Examples include annual insurance premiums, planned travel, or vehicle maintenance. Setting aside a small amount regularly can make large planned expenses easier to manage without relying entirely on borrowing."
    },
    {
        "instruction": "How can someone distinguish between fixed and variable expenses?",
        "response": "Fixed expenses usually remain similar from month to month, such as rent or a fixed loan EMI. Variable expenses change based on usage or consumption, such as groceries, electricity, and transportation. Categorizing expenses helps with budgeting and identifying areas where spending may be adjusted."
    },
    {
        "instruction": "A person spends Rs. 6,000 on groceries, Rs. 2,000 on transport, and Rs. 1,500 on utilities. Calculate total monthly expenses for these categories.",
        "response": "Total Expenses = Groceries + Transport + Utilities. Total Expenses = Rs. 6,000 + Rs. 2,000 + Rs. 1,500 = Rs. 9,500."
    },
    {
        "instruction": "What is an opportunity cost in personal finance?",
        "response": "Opportunity cost is the value of the next best alternative that a person gives up when making a decision. For example, spending money on an expensive purchase may mean giving up the opportunity to save or use that money for another goal."
    },
    {
        "instruction": "How can a person prepare a budget when their monthly income changes?",
        "response": "They can estimate a conservative baseline income using their reliable earnings, prioritize essential expenses, and keep flexible spending within the remaining amount. During higher-income months, they can allocate additional money toward savings, debt repayment, or planned expenses. Maintaining a cash reserve can help manage lower-income months."
    },
    {
        "instruction": "What is lifestyle inflation?",
        "response": "Lifestyle inflation occurs when a person's spending increases as their income increases. For example, someone may move to a more expensive home or increase discretionary purchases after receiving a salary increase. If spending rises as quickly as income, the person may not improve their savings rate."
    },
    {
        "instruction": "A person earns Rs. 30,000 monthly and wants to save Rs. 5,000. What is the maximum amount available for expenses?",
        "response": "Available Expenses = Monthly Income - Planned Savings. Available Expenses = Rs. 30,000 - Rs. 5,000 = Rs. 25,000. This assumes there are no other planned allocations."
    },

    # FINANCIAL CALCULATIONS (9 examples)

    {
        "instruction": "Calculate 8% of Rs. 25,000.",
        "response": "Percentage Amount = Total Amount × Percentage / 100. Calculation = 25,000 × 8 / 100 = Rs. 2,000."
    },
    {
        "instruction": "An item costs Rs. 4,000 and is sold at a 15% discount. Calculate the discounted price.",
        "response": "Discount = 4,000 × 15 / 100 = Rs. 600. Discounted Price = Rs. 4,000 - Rs. 600 = Rs. 3,400."
    },
    {
        "instruction": "A person's monthly salary increases from Rs. 40,000 to Rs. 46,000. Calculate the percentage increase.",
        "response": "Increase = Rs. 46,000 - Rs. 40,000 = Rs. 6,000. Percentage Increase = (6,000 / 40,000) × 100 = 15%."
    },
    {
        "instruction": "A person saves Rs. 3,000 every month for 12 months. How much do they save in total, excluding interest?",
        "response": "Total Savings = Monthly Savings × Number of Months. Total Savings = Rs. 3,000 × 12 = Rs. 36,000. This excludes any interest earned."
    },
    {
        "instruction": "A person spends Rs. 18,000 out of a monthly income of Rs. 45,000. Calculate the percentage of income spent.",
        "response": "Percentage Spent = (Expenses / Income) × 100. Percentage Spent = (18,000 / 45,000) × 100 = 40%."
    },
    {
        "instruction": "An investment grows from Rs. 10,000 to Rs. 11,500. Calculate the percentage return.",
        "response": "Gain = Rs. 11,500 - Rs. 10,000 = Rs. 1,500. Percentage Return = (Gain / Initial Investment) × 100 = (1,500 / 10,000) × 100 = 15%. This is the total return for the period, not an annualized return."
    },
    {
        "instruction": "A person has assets worth Rs. 8,00,000 and liabilities worth Rs. 3,50,000. Calculate net worth.",
        "response": "Net Worth = Total Assets - Total Liabilities. Net Worth = Rs. 8,00,000 - Rs. 3,50,000 = Rs. 4,50,000."
    },
    {
        "instruction": "A bank account has Rs. 12,000. The customer deposits Rs. 5,000 and withdraws Rs. 3,500. Calculate the closing balance.",
        "response": "Closing Balance = Opening Balance + Deposits - Withdrawals. Closing Balance = Rs. 12,000 + Rs. 5,000 - Rs. 3,500 = Rs. 13,500."
    },
    {
        "instruction": "A person pays Rs. 2,400 in monthly interest on a loan with an outstanding principal of Rs. 4,00,000. Calculate the monthly interest rate.",
        "response": "Monthly Interest Rate = (Monthly Interest / Outstanding Principal) × 100. Rate = (2,400 / 4,00,000) × 100 = 0.6% per month. This is the rate implied by the given figures and does not include fees or other charges."
    }

]


# Confirm the intended batch size
if len(new_examples) != 62:
    raise ValueError(
        f"Expected 60 examples, but found {len(new_examples)}."
    )


# Load existing dataset
if os.path.exists(DATASET_PATH):
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        dataset = json.load(file)
else:
    dataset = []


# Check existing questions
existing_questions = {
    item["instruction"].strip().lower()
    for item in dataset
}

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
    json.dump(dataset, file, indent=4, ensure_ascii=False)


print("Batch 2 expansion completed!")
print("Examples in this batch:", len(new_examples))
print("New examples added:", added)
print("Duplicates skipped:", duplicates)
print("Total dataset examples:", len(dataset))