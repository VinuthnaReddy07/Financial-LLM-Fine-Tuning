import json

DATASET_PATH = "data/financial_dataset.json"

# Load dataset
with open(DATASET_PATH, "r", encoding="utf-8") as file:
    dataset = json.load(file)

# Store the changes
changes = {
    76: {
        "instruction": "How does taking investment risk affect the possibility of earning returns?",
        "response": dataset[76]["response"].replace(
            "riskdoes", "risk does"
        )
    },
    110: {
        "instruction": "How is the debt-to-income ratio calculated?",
        "response": dataset[110]["response"].replace(
            "itto assess", "it to assess"
        )
    }
}

# Update the selected examples
for index, updated_example in changes.items():
    dataset[index]["instruction"] = updated_example["instruction"]
    dataset[index]["response"] = updated_example["response"]

# Save updated dataset
with open(DATASET_PATH, "w", encoding="utf-8") as file:
    json.dump(dataset, file, indent=4, ensure_ascii=False)

print("Dataset updated successfully!")

for index in changes:
    print(f"\nExample {index}:")
    print("Question:", dataset[index]["instruction"])
    print("Answer:", dataset[index]["response"])