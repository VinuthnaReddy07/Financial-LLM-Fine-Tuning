from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Annotated
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from financial_llm.inference import FinancialAssistant
from financial_llm.service import FinancialApplication


class Query(BaseModel):
    question: Annotated[str, Field(min_length=1, max_length=4000)]
    calculation_type: str | None = None
    calculation_inputs: dict[str, Any] | None = None
    use_retrieval: bool = True


class Answer(BaseModel):
    retrieved_facts: list[dict[str, Any]]
    retrieval_status: str
    calculation: dict[str, Any] | None
    model_explanation: str
    uncertainty: list[str]
    disclaimer: str


def create_app(
    assistant: FinancialAssistant | None = None,
    experimental_output_enabled: bool = False,
    application: FinancialApplication | None = None,
) -> FastAPI:
    app = FastAPI(
        title="Local Financial Education Assistant",
        version="1.0.0",
        description=(
            "Experimental local model inference. Outputs are unverified and are "
            "not personalized financial advice."
        ),
    )
    app.state.application = application or (
        FinancialApplication(assistant) if assistant is not None else None
    )
    app.state.experimental_output_enabled = experimental_output_enabled

    @app.get("/health")
    def health() -> dict[str, str | bool]:
        return {
            "status": "ok",
            "model": "ready" if app.state.application is not None else "not_loaded",
            "experimental_output_enabled": app.state.experimental_output_enabled,
        }

    @app.post("/answer", response_model=Answer)
    def answer(query: Query) -> Answer:
        if app.state.application is None:
            raise HTTPException(
                status_code=503,
                detail="No local model is loaded. Start the server with --model-path.",
            )
        if not app.state.experimental_output_enabled:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Unverified model output is disabled. Start the local research "
                    "demo with --enable-experimental-output to opt in."
                ),
            )
        try:
            response = app.state.application.respond(
                query.question,
                calculation_type=query.calculation_type,
                calculation_inputs=query.calculation_inputs,
                use_retrieval=query.use_retrieval,
            )
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        except RuntimeError as error:
            raise HTTPException(status_code=500, detail=str(error)) from error
        return Answer(
            **response,
            disclaimer=(
                "The model explanation is unverified and may be inaccurate. "
                "Retrieved excerpts are limited to the dated citations shown and may "
                "not support every detail; "
                "calculation outputs are separate and assumption-bound. "
                "This is not personalized financial, tax, insurance, or legal advice."
            ),
        )

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the local financial model.")
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--base-model", default=None, help="Required for a LoRA adapter.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--enable-experimental-output",
        action="store_true",
        help="Explicitly enable responses from this unverified research model.",
    )
    args = parser.parse_args()
    assistant = FinancialAssistant(args.model_path, base_model=args.base_model)
    app = create_app(
        assistant,
        experimental_output_enabled=args.enable_experimental_output,
    )
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
