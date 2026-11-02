from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True)
class Citation:
    source_id: str
    title: str
    publisher: str
    url: str
    published_on: str | None
    retrieved_on: str
    review_due_on: str
    stale: bool

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class RetrievedFact:
    text: str
    citation: Citation
    score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "citation": self.citation.to_dict(),
            "relevance_score": round(self.score, 4),
        }


@dataclass(frozen=True)
class RetrievalResult:
    facts: list[RetrievedFact]
    status: str
    uncertainty: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "facts": [fact.to_dict() for fact in self.facts],
            "status": self.status,
            "uncertainty": self.uncertainty,
        }


class FinancialRetriever:
    def __init__(
        self,
        corpus_path: Path,
        *,
        minimum_score: float = 0.15,
        max_results: int = 3,
    ) -> None:
        if not corpus_path.is_file():
            raise FileNotFoundError(f"Curated source corpus not found: {corpus_path}")
        if not 0 <= minimum_score <= 1:
            raise ValueError("minimum_score must be between 0 and 1.")
        if max_results < 1:
            raise ValueError("max_results must be positive.")
        corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
        if not isinstance(corpus, list) or not corpus:
            raise ValueError("Curated source corpus must be a non-empty JSON list.")
        required = {
            "source_id",
            "title",
            "publisher",
            "url",
            "retrieved_on",
            "review_due_on",
            "topic",
            "retrieval_anchors",
            "text",
        }
        for index, document in enumerate(corpus, start=1):
            if not isinstance(document, dict) or not required.issubset(document):
                raise ValueError(f"Curated source {index} is missing required metadata.")
            if not document["text"].strip() or not document["url"].startswith("https://"):
                raise ValueError(f"Curated source {index} has invalid text or URL.")
            anchors = document["retrieval_anchors"]
            if (
                not isinstance(anchors, list)
                or not anchors
                or any(
                    not isinstance(group, list)
                    or not group
                    or any(not isinstance(anchor, str) or not anchor.strip() for anchor in group)
                    for group in anchors
                )
            ):
                raise ValueError(f"Curated source {index} has invalid retrieval anchors.")
            date.fromisoformat(document["retrieved_on"])
            date.fromisoformat(document["review_due_on"])
            if document.get("published_on"):
                date.fromisoformat(document["published_on"])

        self.documents = corpus
        self.minimum_score = minimum_score
        self.max_results = max_results
        self.vectorizer = TfidfVectorizer(
            lowercase=True, ngram_range=(1, 2), stop_words="english"
        )
        self.matrix = self.vectorizer.fit_transform(
            [document["text"] for document in corpus]
        )

    def search(
        self, query: str, *, as_of: date | None = None
    ) -> RetrievalResult:
        if not query.strip():
            raise ValueError("Retrieval query cannot be empty.")
        current_date = as_of or date.today()
        vector = self.vectorizer.transform([query])
        scores = cosine_similarity(vector, self.matrix).ravel()
        ranked = sorted(
            enumerate(scores), key=lambda pair: pair[1], reverse=True
        )
        normalized_query = " ".join(
            re.findall(r"[\w-]+", query.casefold())
        )
        matches = [
            (index, float(score))
            for index, score in ranked
            if score >= self.minimum_score
            and all(
                any(
                    self._contains_anchor(normalized_query, anchor)
                    for anchor in group
                )
                for group in self.documents[index]["retrieval_anchors"]
            )
        ][: self.max_results]
        if not matches:
            return RetrievalResult(
                [],
                "missing",
                "No sufficiently relevant curated source was found. Current or jurisdiction-specific claims remain unverified.",
            )

        facts: list[RetrievedFact] = []
        stale_count = 0
        for index, score in matches:
            document = self.documents[index]
            stale = current_date > date.fromisoformat(document["review_due_on"])
            stale_count += stale
            citation = Citation(
                source_id=document["source_id"],
                title=document["title"],
                publisher=document["publisher"],
                url=document["url"],
                published_on=document.get("published_on"),
                retrieved_on=document["retrieved_on"],
                review_due_on=document["review_due_on"],
                stale=stale,
            )
            facts.append(RetrievedFact(document["text"], citation, score))
        if stale_count:
            status = "outdated"
            uncertainty = (
                "One or more keyword-matched sources are past their review date. "
                "A match may not answer every part of the question. Do not rely on "
                "stale material for current terms or rules; verify with the publisher."
            )
        else:
            status = "found"
            uncertainty = (
                "A keyword match is not proof that the excerpt answers every part of "
                "the question. Sources are curated snapshots, not a live check; verify "
                "current terms, legal rules, and personal applicability with the publisher."
            )
        return RetrievalResult(facts, status, uncertainty)

    @staticmethod
    def _contains_anchor(query: str, anchor: str) -> bool:
        normalized_anchor = " ".join(re.findall(r"[\w-]+", anchor.casefold()))
        return f" {normalized_anchor} " in f" {query} "
