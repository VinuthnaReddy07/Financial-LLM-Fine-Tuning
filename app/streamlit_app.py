from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from financial_llm.inference import FinancialAssistant  # noqa: E402
from financial_llm.calculations import CALCULATORS  # noqa: E402
from financial_llm.service import FinancialApplication  # noqa: E402

st.set_page_config(page_title="Financial Education Assistant", page_icon="₹")
st.title("Financial Education Assistant")
st.warning(
    "The model explanation is unverified and may be inaccurate. Retrieved source "
    "facts and tool calculations are displayed separately. This is not personalized "
    "financial, tax, insurance, or legal advice. "
    "Do not enter account numbers, passwords, OTPs, or other sensitive information."
)

default_model_path = ROOT / "models" / "full_finetuned_gpt2_eos"
model_path = Path(os.environ.get("FINANCIAL_LLM_MODEL_PATH", str(default_model_path)))
adapter_base = os.environ.get("FINANCIAL_LLM_BASE_MODEL")


@st.cache_resource
def load_application(path: str, base_model: str | None) -> FinancialApplication:
    return FinancialApplication(
        FinancialAssistant(Path(path), base_model=base_model)
    )


try:
    application = load_application(str(model_path), adapter_base)
except (OSError, ValueError, RuntimeError) as error:
    st.error(f"Could not load local model at {model_path}: {error}")
    st.stop()

question = st.text_area(
    "Ask a general financial education question",
    max_chars=4000,
    placeholder="For example: How does compound interest work?",
)
use_retrieval = st.checkbox("Retrieve relevant curated sources", value=True)
calculator_labels = ["No calculation"] + sorted(CALCULATORS)
calculator_type = st.selectbox("Optional deterministic calculation", calculator_labels)
calculation_inputs = None
if calculator_type != "No calculation":
    st.caption("Enter numeric inputs in the units and terms shown in the question.")
    input_text = st.text_input(
        "Calculation inputs as JSON",
        placeholder='{"principal": 10000, "annual_rate_percent": 5, "years": 2}',
    )
    if input_text.strip():
        try:
            parsed_inputs = json.loads(input_text)
            if not isinstance(parsed_inputs, dict):
                raise ValueError("Inputs must be a JSON object.")
            calculation_inputs = parsed_inputs
        except (json.JSONDecodeError, ValueError) as error:
            st.error(f"Invalid calculation input: {error}")
acknowledged = st.checkbox(
    "I understand this is an unverified research model and its answers may be wrong."
)
if st.button(
    "Generate answer",
    type="primary",
    disabled=(
        not question.strip()
        or not acknowledged
        or (calculator_type != "No calculation" and calculation_inputs is None)
    ),
):
    with st.spinner("Generating locally..."):
        try:
            result = application.respond(
                question,
                calculation_type=(
                    None if calculator_type == "No calculation" else calculator_type
                ),
                calculation_inputs=calculation_inputs,
                use_retrieval=use_retrieval,
            )
            st.subheader("Retrieved source excerpts (may be partial)")
            if result["retrieved_facts"]:
                for fact in result["retrieved_facts"]:
                    citation = fact["citation"]
                    st.markdown(
                        f"- {fact['text']}  \n"
                        f"  Source: [{citation['title']}]({citation['url']}) "
                        f"({citation['publisher']}; retrieved {citation['retrieved_on']}; "
                        f"review due {citation['review_due_on']})"
                        f"{' — OUTDATED' if citation['stale'] else ''}"
                    )
            else:
                st.info(
                    "No sufficiently relevant curated source was found; "
                    "current or jurisdiction-specific claims remain unverified."
                )
            if result["calculation"]:
                st.subheader("Deterministic calculation")
                st.json(result["calculation"])
            st.subheader("Model-generated explanation (unverified)")
            st.markdown(result["model_explanation"])
            st.subheader("Uncertainty")
            for note in result["uncertainty"]:
                st.write(f"- {note}")
        except (ValueError, RuntimeError, FileNotFoundError) as error:
            st.error(str(error))
