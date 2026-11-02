import json
from collections import Counter
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATASET_PATH = Path("data/financial_dataset.json")


# 1. Load dataset
with open(DATASET_PATH, "r", encoding="utf-8") as file:
    dataset = json.load(file)

print("=" * 55)
print("FINANCIAL DATASET QUALITY AUDIT")
print("=" * 55)

print("Total examples:", len(dataset))


# 2. Check structure and missing values
required_fields = {"instruction", "response"}

invalid_records = []
empty_instructions = []
empty_responses = []

for index, item in enumerate(dataset):

    if not isinstance(item, dict):
        invalid_records.append(index)
        continue

    if not required_fields.issubset(item.keys()):
        invalid_records.append(index)
        continue

    if not isinstance(item["instruction"], str):
        invalid_records.append(index)
        continue

    if not isinstance(item["response"], str):
        invalid_records.append(index)
        continue

    if not item["instruction"].strip():
        empty_instructions.append(index)

    if not item["response"].strip():
        empty_responses.append(index)


print("\n1. STRUCTURE CHECK")
print("Invalid records:", len(invalid_records))
print("Empty instructions:", len(empty_instructions))
print("Empty responses:", len(empty_responses))


# Stop if records cannot be safely processed
if invalid_records:
    print("\nInvalid record indexes:", invalid_records)
    raise ValueError("Fix invalid records before continuing.")

if empty_instructions or empty_responses:
    raise ValueError("Fix empty instructions or responses first.")


# 3. Check exact duplicate instructions
normalized_questions = [
    item["instruction"].strip().lower()
    for item in dataset
]

question_counts = Counter(normalized_questions)

duplicate_questions = {
    question: count
    for question, count in question_counts.items()
    if count > 1
}

print("\n2. EXACT DUPLICATE QUESTIONS")
print("Duplicate question groups:", len(duplicate_questions))

for question, count in duplicate_questions.items():
    print(f"- {question} ({count} times)")


# 4. Check repeated responses
normalized_responses = [
    item["response"].strip().lower()
    for item in dataset
]

response_counts = Counter(normalized_responses)

duplicate_responses = {
    response: count
    for response, count in response_counts.items()
    if count > 1
}

print("\n3. EXACT DUPLICATE RESPONSES")
print("Duplicate response groups:", len(duplicate_responses))

for response, count in duplicate_responses.items():
    print(f"- {response[:150]}... ({count} times)")


# 5. Check response lengths
short_responses = []
long_responses = []

for index, item in enumerate(dataset):

    word_count = len(item["response"].split())

    if word_count < 20:
        short_responses.append((index, word_count))

    if word_count > 200:
        long_responses.append((index, word_count))


print("\n4. RESPONSE LENGTH CHECK")
print("Responses below 20 words:", len(short_responses))
print("Responses above 200 words:", len(long_responses))

for index, count in short_responses:
    print(f"- Example {index}: {count} words")

for index, count in long_responses:
    print(f"- Example {index}: {count} words")


# 6. Find potentially similar questions
questions = [
    item["instruction"]
    for item in dataset
]

vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    stop_words="english"
)

question_vectors = vectorizer.fit_transform(questions)

similarity_matrix = cosine_similarity(question_vectors)

similar_pairs = []

for i in range(len(questions)):
    for j in range(i + 1, len(questions)):

        similarity = similarity_matrix[i][j]

        if similarity >= 0.80:
            similar_pairs.append(
                (i, j, round(float(similarity), 3))
            )


print("\n5. POTENTIALLY SIMILAR QUESTIONS")
print("Similar question pairs:", len(similar_pairs))

for i, j, score in similar_pairs:
    print(f"\nSimilarity: {score}")
    print(f"Example {i}: {questions[i]}")
    print(f"Example {j}: {questions[j]}")


# 7. Final summary
print("\n" + "=" * 55)
print("AUDIT SUMMARY")
print("=" * 55)

print("Total examples:", len(dataset))
print("Invalid records:", len(invalid_records))
print("Empty instructions:", len(empty_instructions))
print("Empty responses:", len(empty_responses))
print("Exact duplicate questions:", len(duplicate_questions))
print("Exact duplicate responses:", len(duplicate_responses))
print("Short responses:", len(short_responses))
print("Long responses:", len(long_responses))
print("Potentially similar question pairs:", len(similar_pairs))

print("\nAudit completed.")
print("Review the warnings before modifying the dataset.")