import json

with open("data/financial_dataset.json", "r", encoding="utf-8") as file:
    dataset = json.load(file)

indexes = [41, 76, 48, 110]

for index in indexes:

    print("\n" + "=" * 50)
    print("EXAMPLE:", index)

    print("Question:")
    print(dataset[index]["instruction"])

    print("\nAnswer:")
    print(dataset[index]["response"])