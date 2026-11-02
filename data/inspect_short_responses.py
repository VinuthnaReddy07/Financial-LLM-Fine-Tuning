import json

with open("data/financial_dataset.json", "r", encoding="utf-8") as file:
    dataset = json.load(file)

print("SHORT RESPONSE REVIEW")
print("=" * 60)

for index, item in enumerate(dataset):
    word_count = len(item["response"].split())

    if word_count < 20:
        print(f"\nExample {index} | Words: {word_count}")
        print("Question:", item["instruction"])
        print("Answer:", item["response"])