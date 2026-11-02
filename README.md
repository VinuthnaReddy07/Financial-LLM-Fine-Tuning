# Local Financial Education LLM

[![Tests](https://github.com/VinuthnaReddy07/Financial-LLM-Fine-Tuning/actions/workflows/tests.yml/badge.svg)](https://github.com/VinuthnaReddy07/Financial-LLM-Fine-Tuning/actions/workflows/tests.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A local research project for preparing financial education datasets, fine-tuning GPT-2, and evaluating and demonstrating model responses.

> **Research prototype—not financial advice.** Model answers are unverified, human review is incomplete, and this project does not pass its release gate. Do not use it to make financial decisions.

## What’s included

- Reviewed dataset preparation, grouped splits, and response-only tokenization
- Full and LoRA fine-tuning workflows
- Local FastAPI and Streamlit demos
- Optional Decimal-based calculations and dated source retrieval
- An independent 110-question evaluation benchmark

The calculator and source retrieval do not make model-generated answers reliable. Existing checkpoints predate the reviewed dataset. See the [evaluation report](reports/evaluation/financial_benchmark_v2_final.md) for measured results and limitations.

## Quick start

Requires Python 3.11 or newer. Model weights are not included; provide compatible local model files for training or inference.

```powershell
py -3.11 -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -e ".[dev]"
.\venv\Scripts\python.exe -m pytest
```

For CUDA, install the PyTorch build appropriate for your machine before installing the project.

## Run a local demo

Point the app to a compatible local checkpoint. For a LoRA adapter, also set its base model:

```powershell
$env:FINANCIAL_LLM_MODEL_PATH = "models\experiments\lora-v1\final"
$env:FINANCIAL_LLM_BASE_MODEL = "openai-community/gpt2"
.\venv\Scripts\python.exe -m streamlit run app\streamlit_app.py
```

The API is disabled for answer generation by default and binds to loopback. Keep it local; it has no authentication.

## Project status

The automated test suite has 91 tests, but passing tests do not establish answer accuracy. The benchmark found low model numeric coverage, and human evaluation remains outstanding. Do not present this model as validated or suitable for consequential use.

## Documentation

- [Architecture](docs/architecture.md)
- [Dataset and provenance](docs/data-card.md)
- [Model card](docs/model-card.md)
- [Evaluation results and guidance](docs/evaluation.md)
- [Human evaluation guide](docs/human-evaluation-guide.md)
- [Final quality audit](reports/evaluation/final_quality_audit_2026-11-01.md)
- [Regulatory source notes](docs/regulatory-source-notes.md)
- [Contributing](CONTRIBUTING.md)

The MIT license covers original project software only. Dataset contents, source excerpts, and model artifacts may have separate rights or usage restrictions; review the data card and source notes before reuse.
