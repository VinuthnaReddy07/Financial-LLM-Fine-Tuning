from __future__ import annotations

from pathlib import Path
from typing import Any

from financial_llm.calculations import calculate
from financial_llm.inference import FinancialAssistant
from financial_llm.retrieval import FinancialRetriever

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_CORPUS = (
    PROJECT_ROOT / "data" / "curated" / "financial_sources_v1.json"
)


class FinancialApplication:
    def __init__(
        self,
        assistant: FinancialAssistant,
        retriever: FinancialRetriever | None = None,
    ) -> None:
        self.assistant = assistant
        self.retriever = retriever or FinancialRetriever(DEFAULT_SOURCE_CORPUS)

    def respond(
        self,
        question: str,
        *,
        calculation_type: str | None = None,
        calculation_inputs: dict[str, Any] | None = None,
        use_retrieval: bool = True,
    ) -> dict[str, Any]:
        if not question.strip():
            raise ValueError("Question cannot be empty.")
        if calculation_type is None and calculation_inputs is not None:
            raise ValueError("calculation_type is required when calculation_inputs are supplied.")
        if calculation_type is not None:
            if not calculation_type.strip():
                raise ValueError("calculation_type cannot be empty.")
            if calculation_inputs is None:
                raise ValueError("calculation_inputs are required for a calculation.")
        calculation = (
            calculate(calculation_type, calculation_inputs or {})
            if calculation_type
            else None
        )
        retrieval = (
            self.retriever.search(question)
            if use_retrieval
            else None
        )
        model_context = self._model_context(calculation, retrieval)
        explanation = self.assistant.generate(question, context=model_context)
        uncertainty: list[str] = []
        if retrieval is None:
            uncertainty.append("Retrieval was not requested; factual claims are unverified.")
        else:
            uncertainty.append(retrieval.uncertainty)
        if calculation is None:
            uncertainty.append(
                "No deterministic calculation tool was invoked; any arithmetic in the model explanation is unverified."
            )
        else:
            uncertainty.append(
                "The calculation is an arithmetic result under the listed assumptions, not financial, tax, or legal advice."
            )
        return {
            "retrieved_facts": (
                [fact.to_dict() for fact in retrieval.facts] if retrieval else []
            ),
            "retrieval_status": retrieval.status if retrieval else "disabled",
            "calculation": calculation.to_dict() if calculation else None,
            "model_explanation": explanation,
            "uncertainty": uncertainty,
        }

    @staticmethod
    def _model_context(calculation: Any, retrieval: Any) -> str:
        sections = [
            "SYSTEM SAFETY CONTEXT: Separate retrieved source facts, deterministic calculations, and your own explanation. Never invent current rules, rates, fees, contacts, legal deadlines, or source claims. Do not treat your generated explanation as verified advice."
        ]
        if retrieval is None:
            sections.append("RETRIEVAL STATUS: Retrieval was disabled. No source was checked.")
        elif retrieval.facts:
            sections.append(
                f"RETRIEVAL STATUS: {retrieval.status}. The lexical match may not "
                "support every requested detail; say so when a source does not answer."
            )
            for fact in retrieval.facts:
                status = "OUTDATED - do not rely on as current" if fact.citation.stale else "curated snapshot"
                sections.append(
                    f"RETRIEVED SOURCE EXCERPT [{fact.citation.source_id}; {fact.citation.publisher}; "
                    f"retrieved {fact.citation.retrieved_on}; {status}]: {fact.text}"
                )
        else:
            sections.append(
                "RETRIEVAL STATUS: No sufficiently relevant source was found. Say the source is missing and avoid asserting current or jurisdiction-specific facts."
            )
        if calculation is None:
            sections.append(
                "CALCULATION STATUS: No deterministic calculation was provided. Do not imply that any arithmetic has been tool-verified."
            )
        else:
            sections.append(
                "CALCULATION RESULT (authoritative only for these supplied inputs): "
                f"{calculation.to_dict()}"
            )
        sections.append(
            "Provide a concise explanation only. Do not alter source facts or calculation values. State missing assumptions and uncertainty."
        )
        return "\n\n".join(sections)
