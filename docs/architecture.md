# Architecture

```mermaid
flowchart LR
    Raw["Preserved raw dataset"] --> Audit["Reviewed canonical builder"]
    Audit --> Canonical["298-record canonical JSON"]
    Canonical --> Split["Near-duplicate-grouped split"]
    Split --> Tokenize["Prompt/response tokenization"]
    Tokenize --> Train["Full fine-tuning or LoRA"]
    Train --> Checkpoint["Unique local experiment output"]
    Checkpoint --> Infer["Shared local inference"]
    Infer --> Service["Financial application service"]
    Service --> Calc["Decimal calculation engine"]
    Service --> Retrieval["Dated curated-source retrieval"]
    Service --> API["FastAPI (loopback by default)"]
    Service --> UI["Streamlit UI"]
    Infer --> Eval["Independent 110-question benchmark"]
    Calc --> Eval
    Retrieval --> Eval
```

Training and inference consume local model files; loading uses `local_files_only=True`. The application service keeps retrieved source excerpts and citations, deterministic calculation outputs and assumptions, and model-generated explanations in separate fields. Retrieval is a small local TF-IDF search over dated curated excerpts and source-specific query anchors; it is not live browsing and can return no source or stale material. The audit found the strict matcher returned only 2/110 benchmark prompts, both partially supported, so it has low recall and does not provide complete coverage. The calculator supports named arithmetic functions only and does not determine legal, tax, investment, or insurance applicability. The API does not include authentication or persistence and should remain on loopback. Generated answers are not independently validated by a fact-checking service.
