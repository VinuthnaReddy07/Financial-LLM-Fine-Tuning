import json

path = "data/financial_dataset.json"

with open(path, "r", encoding="utf-8") as file:
    dataset = json.load(file)

# Example 0: Correct missing space
dataset[0]["response"] = dataset[0]["response"].replace(
    "earnedinterest", "earned interest"
)

# Example 38: Improve question wording
dataset[38]["instruction"] = "What is an expense ratio?"

# Example 206: Correct missing space
dataset[206]["instruction"] = (
    "A business has current assets of Rs. 4,00,000 "
    "and current liabilities of Rs. 2,50,000. "
    "Calculate working capital."
)

print("Corrections applied.")

for index in [0, 38, 206]:
    print(f"\nExample {index}")
    print("Question:", dataset[index]["instruction"])
    print("Answer:", dataset[index]["response"])

with open(path, "w", encoding="utf-8") as file:
    json.dump(dataset, file, indent=4, ensure_ascii=False)

print("\nDataset saved successfully.")