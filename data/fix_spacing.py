import json

path = "data/financial_dataset.json"

with open(path, "r", encoding="utf-8") as file:
    dataset = json.load(file)

response = dataset[76]["response"]

if "beforemaking" in response:
    dataset[76]["response"] = response.replace(
        "beforemaking", "before making"
    )
    print("Spacing corrected!")
else:
    print("Text not found. No changes made.")

with open(path, "w", encoding="utf-8") as file:
    json.dump(dataset, file, indent=4, ensure_ascii=False)

print("\nUpdated response:")
print(repr(dataset[76]["response"]))