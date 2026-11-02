import json

with open("data/financial_dataset.json", "r", encoding="utf-8") as file:
    dataset = json.load(file)

keywords = [
    "calculate",
    "calculation",
    "percentage",
    "interest",
    "principal",
    "rate",
    "profit",
    "loss",
    "return",
    "roi",
    "ratio",
    "income",
    "expense",
    "debt",
    "loan",
    "working capital",
    "net worth",
    "assets",
    "liabilities",
    "savings",
    "discount",
    "investment"
]

print("=" * 65)
print("FINANCIAL CALCULATION AUDIT")
print("=" * 65)

count = 0

for index, item in enumerate(dataset):

    question = item["instruction"].lower()
    answer = item["response"].lower()

    if any(word in question or word in answer for word in keywords):

        print(f"\nExample {index}")
        print("Question:", item["instruction"])
        print("Answer:", item["response"])

        count += 1

print("\n" + "=" * 65)
print("Total matching examples:", count)