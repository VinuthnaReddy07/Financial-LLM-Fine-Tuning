import json
import os

DATASET_PATH = "data/financial_dataset.json"

new_examples = [

    # SECTION 1: STOCKS AND STOCK MARKETS (10)

    {
        "instruction": "What does it mean to own a share of a company?",
        "response": "Owning a share means holding a small ownership interest in a company. Shareholders may benefit if the share price increases or if the company distributes dividends. However, share prices can also decrease, and shareholders may lose some or all of their invested money."
    },
    {
        "instruction": "What is an Initial Public Offering (IPO)?",
        "response": "An Initial Public Offering, or IPO, occurs when a private company offers its shares to the public for the first time and becomes publicly listed, subject to the applicable listing process. Investors can apply for shares through the IPO process, but allotment is not guaranteed and the share price may fluctuate after listing."
    },
    {
        "instruction": "What is a stock exchange?",
        "response": "A stock exchange is an organized marketplace where eligible securities, such as shares, are bought and sold. It provides trading infrastructure, price discovery, and market rules. Examples in India include the National Stock Exchange and the Bombay Stock Exchange."
    },
    {
        "instruction": "What is a bull market?",
        "response": "A bull market generally describes a period when market prices are rising or investor sentiment is positive. Investors may expect continued growth, but market direction can change. A bull market does not mean that every stock will increase in value."
    },
    {
        "instruction": "What is a bear market?",
        "response": "A bear market generally describes a period of significant market decline accompanied by negative investor sentiment. It may occur because of economic uncertainty, declining company earnings, or other factors. During such periods, investment values can fall substantially."
    },
    {
        "instruction": "What is a market index?",
        "response": "A market index measures the performance of a selected group of securities according to a defined methodology. It helps investors understand the overall movement of a particular market or market segment. Examples include the Nifty 50 and BSE Sensex in India."
    },
    {
        "instruction": "What is market capitalization?",
        "response": "Market capitalization is the total market value of a company's outstanding shares. It is calculated by multiplying the current share price by the number of outstanding shares. Market capitalization is commonly used to classify companies by size."
    },
    {
        "instruction": "A company has 10 lakh outstanding shares, and each share is priced at Rs. 50. Calculate its market capitalization.",
        "response": "Market Capitalization = Share Price × Number of Outstanding Shares. Market Capitalization = Rs. 50 × 10,00,000 = Rs. 5,00,00,000, or Rs. 5 crore."
    },
    {
        "instruction": "What is a dividend?",
        "response": "A dividend is a distribution of a portion of a company's earnings or reserves to eligible shareholders, subject to the company's policies and applicable rules. Companies may distribute dividends in cash or other permitted forms. A company is not required to pay dividends regularly."
    },
    {
        "instruction": "What is the difference between a realized gain and an unrealized gain?",
        "response": "An unrealized gain is an increase in an investment's market value while the investment is still held. A realized gain occurs when the investment is sold for more than its purchase cost, after considering relevant costs. Unrealized gains can disappear if market prices decline before the investment is sold."
    },

    # SECTION 2: MUTUAL FUNDS AND EXCHANGE-TRADED FUNDS (10)

    {
        "instruction": "What is a mutual fund?",
        "response": "A mutual fund collects money from multiple investors and invests it in a portfolio of assets according to a stated investment objective. The portfolio may contain stocks, bonds, money market instruments, or other permitted assets. Investors hold units representing their share in the fund."
    },
    {
        "instruction": "What is Net Asset Value (NAV) in a mutual fund?",
        "response": "Net Asset Value, or NAV, represents the per-unit value of a mutual fund's net assets. It is generally calculated by subtracting liabilities from the total value of assets and dividing the result by the number of outstanding units. NAV changes as the value of the fund's holdings changes."
    },
    {
        "instruction": "What is the difference between an ETF and a mutual fund?",
        "response": "An exchange-traded fund, or ETF, is a pooled investment vehicle whose units are traded on a stock exchange during market hours. Traditional mutual fund transactions are generally processed using the applicable NAV. ETFs may require a trading account and can trade at prices that differ slightly from their NAV."
    },
    {
        "instruction": "What is a Systematic Investment Plan (SIP)?",
        "response": "A Systematic Investment Plan, or SIP, is a method of investing a fixed amount in a mutual fund at regular intervals. It encourages disciplined investing and may purchase more units when prices are lower and fewer units when prices are higher. SIPs do not guarantee profits or eliminate market risk."
    },
    {
        "instruction": "Explain rupee cost averaging.",
        "response": "Rupee cost averaging is an approach in which an investor invests a fixed amount at regular intervals. When the unit price is lower, the fixed amount purchases more units; when the price is higher, it purchases fewer units. This can average the purchase cost over time, but it does not guarantee a profit."
    },
    {
        "instruction": "What is an equity mutual fund?",
        "response": "An equity mutual fund primarily invests in shares of companies. Its value can increase or decrease depending on the performance of its investments and market conditions. Equity funds generally involve market risk and may be more suitable for investors with an appropriate risk tolerance and investment horizon."
    },
    {
        "instruction": "What is a debt mutual fund?",
        "response": "A debt mutual fund invests primarily in fixed-income instruments such as government securities, corporate bonds, and money market instruments. Its returns can be affected by interest rate changes, credit quality, and liquidity conditions. Debt funds are not risk-free, and their values can fluctuate."
    },
    {
        "instruction": "What is a fund's expense ratio and how does it affect returns?",
        "response": "The expense ratio represents the annual operating expenses of a fund as a percentage of its assets. These expenses reduce the returns available to investors. For example, a higher expense ratio can reduce an investor's net return compared with an otherwise similar fund having lower expenses."
    },
    {
        "instruction": "What is a fund benchmark?",
        "response": "A benchmark is a reference index or standard used to evaluate a fund's performance. For example, an equity fund may compare its returns with a relevant stock market index. The benchmark should be appropriate for the fund's investment strategy and asset category."
    },
    {
        "instruction": "Why should an investor read a mutual fund's scheme information document?",
        "response": "The scheme information document describes a mutual fund's investment objective, strategy, risks, costs, and operating conditions. Reading it helps investors understand what the fund intends to invest in and the risks involved. It should be reviewed along with current official disclosures and other relevant information."
    },

    # SECTION 3: PORTFOLIO MANAGEMENT AND DIVERSIFICATION (10)

    {
        "instruction": "What is asset allocation?",
        "response": "Asset allocation is the process of dividing an investment portfolio among different asset categories, such as equities, bonds, and cash equivalents. The allocation can depend on investment goals, time horizon, risk tolerance, and financial circumstances. Different allocations have different risk and return characteristics."
    },
    {
        "instruction": "What is portfolio rebalancing?",
        "response": "Portfolio rebalancing means adjusting investments to bring their proportions back toward a chosen asset allocation. For example, if equities increase and become a larger share of a portfolio than intended, an investor may review the allocation and rebalance. Rebalancing can involve transaction costs, taxes, and other considerations."
    },
    {
        "instruction": "What is concentration risk in a portfolio?",
        "response": "Concentration risk occurs when a large portion of a portfolio is invested in a single company, industry, asset, or market. If that investment performs poorly, the portfolio may experience a substantial loss. Diversification can reduce some concentration risk but cannot eliminate all investment risk."
    },
    {
        "instruction": "A portfolio contains Rs. 60,000 in equities and Rs. 40,000 in bonds. Calculate the percentage allocation to each asset.",
        "response": "Total Portfolio Value = Rs. 60,000 + Rs. 40,000 = Rs. 1,00,000. Equity Allocation = (60,000 / 1,00,000) × 100 = 60%. Bond Allocation = (40,000 / 1,00,000) × 100 = 40%."
    },
    {
        "instruction": "An investor has a portfolio worth Rs. 2,00,000. If 25% is allocated to bonds, calculate the bond investment amount.",
        "response": "Bond Allocation = Total Portfolio Value × Allocation Percentage / 100. Bond Allocation = Rs. 2,00,000 × 25 / 100 = Rs. 50,000."
    },
    {
        "instruction": "Why might two investors choose different asset allocations?",
        "response": "Two investors may have different financial goals, time horizons, income stability, existing obligations, and tolerance for investment losses. An investor with a longer time horizon may be comfortable with a different level of market risk than someone who needs money soon. Asset allocation should reflect individual circumstances."
    },
    {
        "instruction": "What is portfolio diversification across industries?",
        "response": "Industry diversification means investing across multiple sectors rather than concentrating investments in one industry. For example, a portfolio may include companies from healthcare, technology, consumer goods, and manufacturing. This can reduce exposure to problems affecting a single industry, although broad market risks remain."
    },
    {
        "instruction": "What is geographic diversification?",
        "response": "Geographic diversification means spreading investments across different countries or regions. It can reduce dependence on the economic conditions of one country. However, international investments may introduce currency, political, regulatory, and market risks."
    },
    {
        "instruction": "What is a portfolio's investment horizon?",
        "response": "An investment horizon is the expected period for which an investor plans to keep money invested before using it. Short-term and long-term goals may require different investment approaches because market fluctuations, liquidity needs, and the time available to recover from losses can differ."
    },
    {
        "instruction": "What should an investor consider before changing their portfolio allocation?",
        "response": "An investor should review whether their financial goals, time horizon, risk tolerance, income, or financial obligations have changed. They should also examine the portfolio's current risk, diversification, transaction costs, taxes, and the reason for making the change. Short-term market movements alone may not justify a major allocation change."
    },

    # SECTION 4: INVESTMENT RISK AND RETURNS (10)

    {
        "instruction": "What is volatility in financial markets?",
        "response": "Volatility describes how much and how frequently an asset's price changes over time. Higher volatility means prices fluctuate more widely. Volatility is one measure of market risk, but it does not describe every possible risk associated with an investment."
    },
    {
        "instruction": "What is standard deviation in investment analysis?",
        "response": "Standard deviation measures how spread out a set of returns is around its average return. In investment analysis, it is often used as a measure of historical return variability. A higher standard deviation indicates greater variation in the measured returns, but it does not predict future performance."
    },
    {
        "instruction": "What is systematic risk?",
        "response": "Systematic risk is the risk that affects a broad financial market or many investments at the same time. Examples include changes in interest rates, inflation, recessions, and major geopolitical events. Diversification across individual securities cannot completely eliminate systematic risk."
    },
    {
        "instruction": "What is unsystematic risk?",
        "response": "Unsystematic risk is risk associated with a particular company, industry, or investment. Examples include management problems, product failures, or company-specific financial difficulties. Diversifying across different companies and industries can reduce some unsystematic risk."
    },
    {
        "instruction": "What is the difference between nominal return and real return?",
        "response": "Nominal return is the percentage change in an investment's value without adjusting for inflation. Real return measures the return after accounting for changes in purchasing power due to inflation. An investment may earn a positive nominal return but a low or negative real return."
    },
    {
        "instruction": "An investment earns a nominal return of 8% while inflation is 5%. Calculate the approximate real return.",
        "response": "The approximate real return is Nominal Return minus Inflation. Approximate Real Return = 8% - 5% = 3%. The more precise calculation is (1.08 / 1.05) - 1, which is approximately 2.86%."
    },
    {
        "instruction": "What is a capital gain?",
        "response": "A capital gain occurs when an asset is sold for more than its purchase cost, after considering relevant costs and adjustments. For example, if an investment is purchased for Rs. 10,000 and sold for Rs. 12,000, the gain before applicable costs and taxes is Rs. 2,000."
    },
    {
        "instruction": "An investor purchases shares for Rs. 15,000 and sells them for Rs. 18,000. Calculate the percentage gain before costs and taxes.",
        "response": "Capital Gain = Selling Value - Purchase Value = Rs. 18,000 - Rs. 15,000 = Rs. 3,000. Percentage Gain = (3,000 / 15,000) × 100 = 20%. This excludes transaction costs and taxes."
    },
    {
        "instruction": "What is a capital loss?",
        "response": "A capital loss occurs when an asset is sold for less than its purchase cost, after considering applicable costs and adjustments. For example, purchasing an investment for Rs. 10,000 and selling it for Rs. 8,000 results in a loss of Rs. 2,000 before additional costs and taxes."
    },
    {
        "instruction": "What is the risk-return trade-off?",
        "response": "The risk-return trade-off describes the relationship between the amount of risk an investor accepts and the return they expect. Investments with higher expected returns often involve greater uncertainty and potential losses. Higher risk does not guarantee higher returns."
    },

    # SECTION 5: INVESTMENT CALCULATIONS AND METRICS (10)

    {
        "instruction": "What is the Compound Annual Growth Rate (CAGR)?",
        "response": "Compound Annual Growth Rate, or CAGR, represents the constant annual growth rate that would take an investment from its beginning value to its ending value over a specified period. It smooths the growth into one annualized figure but does not show the actual fluctuations that occurred during the period."
    },
    {
        "instruction": "An investment grows from Rs. 10,000 to Rs. 14,400 over two years. Calculate its CAGR.",
        "response": "CAGR = (Ending Value / Beginning Value) raised to the power of (1 / Number of Years), minus 1. CAGR = (14,400 / 10,000)^(1/2) - 1 = 1.2 - 1 = 0.20, or 20% per year."
    },
    {
        "instruction": "What is dividend yield?",
        "response": "Dividend yield measures annual dividends per share relative to the current share price. It is calculated as Annual Dividend Per Share divided by Current Share Price, multiplied by 100. Dividend yield can change when the share price or dividend amount changes."
    },
    {
        "instruction": "A company pays an annual dividend of Rs. 5 per share and its share price is Rs. 100. Calculate the dividend yield.",
        "response": "Dividend Yield = (Annual Dividend Per Share / Current Share Price) × 100. Dividend Yield = (5 / 100) × 100 = 5%."
    },
    {
        "instruction": "What is the price-to-earnings ratio?",
        "response": "The price-to-earnings ratio, or P/E ratio, compares a company's share price with its earnings per share. It is calculated as Share Price divided by Earnings Per Share. Investors may use it when evaluating company valuations, but it should be considered alongside growth, risk, industry conditions, and other financial information."
    },
    {
        "instruction": "A company has a share price of Rs. 240 and earnings per share of Rs. 12. Calculate its P/E ratio.",
        "response": "P/E Ratio = Share Price / Earnings Per Share. P/E Ratio = 240 / 12 = 20. The company is trading at 20 times its earnings per share."
    },
    {
        "instruction": "What is return on investment (ROI)?",
        "response": "Return on Investment, or ROI, measures the gain or loss relative to the cost of an investment. A common formula is ROI = (Net Gain / Investment Cost) × 100. The result depends on how costs, income, and the investment period are defined."
    },
    {
        "instruction": "An investment costs Rs. 20,000 and produces a net gain of Rs. 3,000. Calculate ROI.",
        "response": "ROI = (Net Gain / Investment Cost) × 100. ROI = (3,000 / 20,000) × 100 = 15%."
    },
    {
        "instruction": "What is the Sharpe ratio?",
        "response": "The Sharpe ratio measures an investment's excess return relative to its volatility. A common formula is (Portfolio Return - Risk-Free Rate) divided by the Standard Deviation of Portfolio Returns. It is one way to compare risk-adjusted performance, but it depends on the selected period and assumptions."
    },
    {
        "instruction": "A portfolio returns 12%, the risk-free rate is 4%, and the portfolio standard deviation is 10%. Calculate the Sharpe ratio.",
        "response": "Sharpe Ratio = (Portfolio Return - Risk-Free Rate) / Standard Deviation. Sharpe Ratio = (12% - 4%) / 10% = 8% / 10% = 0.8."
    },

    # SECTION 6: PRACTICAL INVESTMENT SCENARIOS AND RESPONSIBLE AI (10)

    {
        "instruction": "A person invests all their savings in one company's shares. What risk does this create?",
        "response": "Investing all savings in one company's shares creates significant concentration risk. If the company experiences financial problems or its share price declines, a large portion of the person's savings may lose value. Diversification can reduce dependence on a single investment, although it cannot eliminate all market risk."
    },
    {
        "instruction": "An investor becomes worried because their mutual fund value falls for two consecutive days. What should they understand?",
        "response": "Short-term price movements are a normal feature of market-linked investments. Two days of declining value do not by themselves establish whether an investment is suitable or unsuitable. The investor should review the fund's objective, risk level, investment horizon, and their financial needs rather than reacting only to short-term movements."
    },
    {
        "instruction": "A person wants to invest money that they will need for rent next month. What important factor should they consider?",
        "response": "Money needed for an essential expense next month generally requires high liquidity and low exposure to short-term market fluctuations. Market-linked investments can lose value and may not be suitable for money needed immediately. The person should consider the timing and certainty of the expense before deciding where to keep the money."
    },
    {
        "instruction": "An investor sees an online advertisement promising guaranteed monthly stock market returns. How should they evaluate it?",
        "response": "They should treat guaranteed high-return claims with caution because market-linked investments involve risk. They should verify the organization and its regulatory status through official sources, examine the terms, and avoid transferring money based on pressure or unsupported promises. They should never share banking passwords, PINs, or OTPs."
    },
    {
        "instruction": "A person wants to compare two mutual funds. Which factors should they examine?",
        "response": "They can compare the funds' investment objectives, portfolio holdings, risk levels, expense ratios, benchmark performance, fund manager approach, and consistency across relevant periods. They should also consider whether each fund fits their time horizon and financial needs. Past performance does not guarantee future returns."
    },
    {
        "instruction": "An investor's portfolio is heavily invested in technology companies. What could happen if the technology sector performs poorly?",
        "response": "A portfolio heavily concentrated in technology companies may experience a larger decline if that sector faces weak demand, regulatory changes, valuation declines, or other difficulties. This is an example of sector concentration risk. Exposure to other industries and asset classes may reduce some of this risk."
    },
    {
        "instruction": "A person wants to withdraw money from an investment but the investment has an exit fee. What should they examine?",
        "response": "They should review the exit fee, lock-in period, withdrawal rules, taxes, current investment value, and the reason for withdrawing. They should compare the total cost of withdrawal with their liquidity needs. The specific conditions depend on the investment product."
    },
    {
        "instruction": "Why should investors avoid making decisions only because a stock's price has recently increased?",
        "response": "A recent price increase does not establish that a stock is fairly valued or will continue rising. Investors should examine company fundamentals, valuation, risks, market conditions, and their own investment objectives. Buying only because of recent price movements can lead to decisions driven by momentum or fear of missing out."
    },
    {
        "instruction": "A user asks a financial AI assistant to predict the exact closing price of a stock next month. How should it respond?",
        "response": "The assistant should explain that it cannot reliably predict an exact future stock price. Prices are affected by uncertain company, economic, market, and geopolitical factors. It may explain historical data, valuation concepts, and sources of uncertainty, but it should not present speculative predictions as guaranteed facts."
    },
    {
        "instruction": "A financial AI assistant receives a question about current mutual fund returns, but it has no access to live financial data. What should it do?",
        "response": "The assistant should clearly state that it cannot verify current mutual fund returns without access to up-to-date data. It should avoid inventing performance figures or presenting old information as current. It can explain how to check official fund factsheets, disclosures, and other reliable sources."
    }

]


# Verify batch size before changing the dataset
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


# Identify existing instructions
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


print("Batch 3 expansion completed!")
print("Examples in this batch:", len(new_examples))
print("New examples added:", added)
print("Duplicates skipped:", duplicates)
print("Total dataset examples:", len(dataset))