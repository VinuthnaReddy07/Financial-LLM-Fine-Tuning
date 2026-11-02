# Local Financial Education Language Model

[![Tests](https://github.com/VinuthnaReddy07/Financial-LLM-Fine-Tuning/actions/workflows/tests.yml/badge.svg)](https://github.com/VinuthnaReddy07/Financial-LLM-Fine-Tuning/actions/workflows/tests.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A local-only project for preparing a reviewed financial education dataset, training GPT-2 with full fine-tuning or LoRA, evaluating model responses, and serving a small educational demo. It is not a financial product or a source of personalized financial, tax, insurance, or legal advice.

> **Research prototype — not for consequential use.** Model answers are unverified, the project does not pass its release gate, and human evaluation remains outstanding. Do not rely on its output for financial decisions.

The [MIT License](LICENSE) applies to original project software. Dataset material, source excerpts, and model artifacts may have separate rights or usage restrictions; review the [data card](docs/data-card.md) and [regulatory source notes](docs/regulatory-source-notes.md) before reuse.

## Status

The original dataset and existing model artifacts are preserved. The reviewed dataset pipeline, grouped splits, response-only tokenization, training runner, local inference module, FastAPI endpoint, and Streamlit UI are in place. FastAPI and Streamlit answer workflows have automated integration tests. Model answer quality remains unverified pending human review; the project does not pass its release gate.

The existing checkpoints and reports predate the reviewed 298-record dataset. Their presence is not evidence that they were trained or evaluated on the new dataset.

An independent 110-question evaluation benchmark now covers all 11 project topics, including 40 arithmetic cases. A Decimal-based calculation engine and a dated local-source retriever are integrated into the FastAPI backend and Streamlit UI. These external components can improve application-level traceability and arithmetic, but they do **not** make GPT-2 itself more accurate. See the [final benchmark report](reports/evaluation/financial_benchmark_v2_final.md) for measured results and limitations.

Latest measured v2 outputs (all 110 questions; automated number-presence is not an accuracy score):

| Arm | Expected numbers present in model text | Calculator expected values exact | Historical retrieval matches |
|---|---:|---:|---:|
| Base GPT-2 | 1/70 | N/A | N/A |
| Full-v2 | 5/70 | N/A | N/A |
| Base + calculator | 0/70 | 70/70 | N/A |
| Base + retrieval | 1/70 | N/A | 37/110 |
| Base + retrieval + calculator | 0/70 | 70/70 | 37/110 |
| LoRA-v2 | 1/70 | N/A | N/A |

The original six report JSON/CSV files are preserved. A post-run retrieval audit found unrelated keyword matches in the historical retrieval outputs, so the current retriever now requires curated source-scope anchors; that stricter filter matched 2/110 benchmark prompts (both partial scope matches), not the historical 37. The old reports have not been rewritten to reflect the new matcher. See the [final quality audit](reports/evaluation/final_quality_audit_2026-11-01.md).

Final audit validation: **91 automated tests passed**. The suite includes calculator edge cases, retrieval source/uncertainty behavior, and FastAPI and Streamlit workflows with a fake model. It does not constitute a human accuracy review or validate real model-generated answers.

## Requirements

- Python 3.11 or newer
- PyTorch; CUDA is optional
- Local tokenizer/model files for the base GPT-2 model and, when running inference, a compatible fine-tuned checkpoint. Model loading is local-only; this repository does not include model weight files.
- Install the project and development dependencies in a virtual environment:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -e ".[dev]"
```

If the default package index does not provide the desired CUDA-enabled PyTorch build, install the appropriate PyTorch build before installing the project.

## Dataset pipeline

The input under `data/raw/` is preserved. The 298-record reviewed derivative is `data/validated/financial_dataset_v1.json`; the 238/30/30 grouped train, validation, and test splits are under `data/processed/`. The tokenized files preserve EOS and mask instruction tokens from the loss.

The builder and split/tokenization commands refuse to overwrite existing outputs. For a fresh rerun, provide new output paths:

```powershell
$env:PYTHONPATH = "src"
.\venv\Scripts\python.exe -m financial_llm.data.build_canonical_dataset `
  --source data\raw\financial_dataset_expanded_305_raw.json `
  --output data\validated\financial_dataset_v2.json `
  --audit-json reports\dataset_quality\dataset_audit_v2.json `
  --audit-markdown reports\dataset_quality\dataset_quality_v2.md
.\venv\Scripts\python.exe -m financial_llm.data.split_dataset `
  --source data\validated\financial_dataset_v2.json `
  --output-dir data\processed_v2
.\venv\Scripts\python.exe -m financial_llm.data.tokenize_dataset `
  --input-dir data\processed_v2 `
  --output-dir data\processed_v2\tokenized
```

Check the source/options before rerunning a stage. Never point an output at an original, archive, checkpoint, or existing report.

## Tests

```powershell
.\venv\Scripts\python.exe -m pytest
```

The same test suite runs automatically on pushes and pull requests with GitHub Actions.

## Training

Training outputs are written to a new directory and existing output directories are rejected. The base model must already be available locally:

```powershell
$env:PYTHONPATH = "src"
.\venv\Scripts\python.exe -m financial_llm.training.train `
  --family lora `
  --output-dir models\experiments\lora-v1
```

Use `--family full` for full fine-tuning. Both workflows use the same reviewed tokenized partitions and training configuration. Check available disk/GPU memory before starting; no training run is performed by importing the project.

## Evaluation

`data/evaluation/financial_benchmark_v2.json` is separate from the training split and contains 110 questions (10 per topic), including 40 independently checked calculation cases and conceptual, factual, multi-step, and uncertainty prompts. The v2 comparison runner uses the same benchmark and generation settings for each model/tool arm; outputs are new files and existing evaluation reports are preserved.

Run individual arms with unique output names:

```powershell
$env:PYTHONPATH = "src"
.\venv\Scripts\python.exe -m financial_llm.evaluation.run_benchmark `
  --arm base `
  --model-path openai-community/gpt2 `
  --benchmark data\evaluation\financial_benchmark_v2.json `
  --output reports\evaluation\benchmark_v2\v2-base-alone.json
.\venv\Scripts\python.exe -m financial_llm.evaluation.run_benchmark `
  --arm full `
  --model-path models\experiments\full-v2\final `
  --benchmark data\evaluation\financial_benchmark_v2.json `
  --output reports\evaluation\benchmark_v2\v2-full-v2-alone.json
.\venv\Scripts\python.exe -m financial_llm.evaluation.run_benchmark `
  --arm calculator `
  --model-path openai-community/gpt2 `
  --benchmark data\evaluation\financial_benchmark_v2.json `
  --output reports\evaluation\benchmark_v2\v2-base-calculator.json
.\venv\Scripts\python.exe -m financial_llm.evaluation.run_benchmark `
  --arm retrieval `
  --model-path openai-community/gpt2 `
  --benchmark data\evaluation\financial_benchmark_v2.json `
  --output reports\evaluation\benchmark_v2\v2-base-retrieval.json
.\venv\Scripts\python.exe -m financial_llm.evaluation.run_benchmark `
  --arm retrieval_calculator `
  --model-path openai-community/gpt2 `
  --benchmark data\evaluation\financial_benchmark_v2.json `
  --output reports\evaluation\benchmark_v2\v2-base-retrieval-calculator.json
.\venv\Scripts\python.exe -m financial_llm.evaluation.run_benchmark `
  --arm lora `
  --model-path models\experiments\lora-v2\final `
  --base-model openai-community/gpt2 `
  --benchmark data\evaluation\financial_benchmark_v2.json `
  --output reports\evaluation\benchmark_v2\v2-lora-v2-alone.json
```

The benchmark builder is `src/financial_llm/evaluation/build_benchmark_v2.py` and refuses to overwrite an existing output. Existing comparison CSVs are preserved. To create separate review sheets with fields for factual correctness, relevance, completeness, calculation correctness, grounding, and safety:

```powershell
$env:PYTHONPATH = "src"
.\venv\Scripts\python.exe -m financial_llm.evaluation.build_human_review_sheets
```

The command writes six new sheets under `reports\evaluation\benchmark_v2\human_review_v2\` and refuses to overwrite them. Use a new `--output-dir` to create another set. Exact training-prompt matches and high TF-IDF similarity are leakage-screening signals; inspect them before interpreting results. Model numeral coverage is not a factual-accuracy score. Tool outputs are compared separately against expected values. The [human evaluation guide](docs/human-evaluation-guide.md) defines the six 0–5 scoring criteria and examples.

## Application calculation and retrieval

The Python calculation engine supports 20 named arithmetic operations and returns formulas, assumptions, and separately formatted values. It does not choose tax rates, interpret policy coverage, or make suitability determinations. The curated local retrieval corpus is `data/curated/financial_sources_v1.json`; each excerpt has publisher, URL, review dates, and query-scope anchors. Retrieval is not live browsing: no-match and past-review-date sources are surfaced as uncertainty, and a lexical/anchor match still may not fully support the question. Retrieved source excerpts, calculator results, and generated explanations are shown separately in the UI and API. Add a source only after checking its authority, scope, date, and permitted use. See [source notes](docs/regulatory-source-notes.md).

## Local interfaces

The full-v2 benchmark failed to produce reliable answers (including both exact calculation checks). The interfaces therefore treat generated text as unverified research output and require an explicit acknowledgement/opt-in. Do not rely on or publish answers from these checkpoints. See the [manual review](reports/evaluation/full-v2_manual_review.md).

The default demo checkpoint is the pre-existing `models/full_finetuned_gpt2_eos`; it is a legacy artifact and is not the new v1 training output. Select a different local checkpoint without changing files:

```powershell
$env:FINANCIAL_LLM_MODEL_PATH = "models\experiments\lora-v1\final"
$env:FINANCIAL_LLM_BASE_MODEL = "openai-community/gpt2"
.\venv\Scripts\python.exe -m streamlit run app\streamlit_app.py
```

Run the API on loopback:

```powershell
$env:PYTHONPATH = "src"
.\venv\Scripts\python.exe -m app.api `
  --model-path models\experiments\lora-v1\final `
  --base-model openai-community/gpt2 `
  --enable-experimental-output
```

OpenAPI docs are available at `http://127.0.0.1:8000/docs`. Without `--enable-experimental-output`, the API refuses to generate answers. The API has no authentication; keep it on loopback and do not expose it to a public or untrusted network. The interface does not save conversation history. Do not enter credentials, account numbers, OTPs, or other sensitive information.

## Project documentation

- [Data card](docs/data-card.md)
- [Expansion batch 2 static review](docs/expansion-batch-2-review.md)
- [Model card](docs/model-card.md)
- [Evaluation guidance](docs/evaluation.md)
- [Human evaluation guide](docs/human-evaluation-guide.md)
- [Regulatory source notes](docs/regulatory-source-notes.md)
- [Architecture](docs/architecture.md)
- [Project status and remaining release checks](docs/project_status.md)
- [Final quality audit](reports/evaluation/final_quality_audit_2026-11-01.md)
- [Contributing](CONTRIBUTING.md)
- [MIT License](LICENSE)
