from __future__ import annotations

import os
import threading
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from financial_llm.data.dataset import prompt_for


class FinancialAssistant:
    def __init__(
        self,
        model_path: str | Path,
        base_model: str | None = None,
        max_new_tokens: int = 100,
        repetition_penalty: float = 1.1,
        no_repeat_ngram_size: int = 3,
    ) -> None:
        model_location = str(model_path)
        local_model_path = Path(model_path)
        model_exists_locally = local_model_path.exists()
        if not model_exists_locally and (
            "\\" in model_location or "/" not in model_location
        ):
            raise FileNotFoundError(
                f"Model path does not exist and is not a cached model identifier: "
                f"{model_path}"
            )
        if model_exists_locally and not local_model_path.is_dir():
            raise ValueError(f"Model path must be a directory: {model_path}")
        if max_new_tokens < 1:
            raise ValueError("max_new_tokens must be positive.")
        if repetition_penalty < 1:
            raise ValueError("repetition_penalty must be at least 1.")
        if no_repeat_ngram_size < 0:
            raise ValueError("no_repeat_ngram_size cannot be negative.")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        dtype = torch.float16 if self.device.type == "cuda" else torch.float32
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_location, local_files_only=True
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token

        is_adapter = model_exists_locally and (
            local_model_path / "adapter_config.json"
        ).is_file()
        if is_adapter:
            if not base_model:
                raise ValueError("Loading a LoRA adapter requires a base_model.")
            model = AutoModelForCausalLM.from_pretrained(
                base_model,
                dtype=dtype,
                local_files_only=True,
            )
            self.model = PeftModel.from_pretrained(
                model, model_location, local_files_only=True
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_location,
                dtype=dtype,
                local_files_only=True,
            )
        self.model.to(self.device)
        self.model.eval()
        self.max_new_tokens = max_new_tokens
        self.repetition_penalty = repetition_penalty
        self.no_repeat_ngram_size = no_repeat_ngram_size
        context_limit = getattr(self.model.config, "n_positions", None)
        if context_limit is None:
            context_limit = getattr(self.model.config, "max_position_embeddings", None)
        if context_limit is None:
            raise ValueError("Model configuration does not define a context limit.")
        self.context_limit = int(context_limit)
        self._generation_lock = threading.Lock()

    def generate(self, instruction: str, *, context: str | None = None) -> str:
        if not instruction.strip():
            raise ValueError("Instruction cannot be empty.")
        prompt_instruction = instruction
        if context:
            prompt_instruction = f"{instruction}\n\n{context}"
        prompt = prompt_for(prompt_instruction)
        inputs = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
        input_length = inputs["input_ids"].shape[1]
        if input_length + self.max_new_tokens > self.context_limit:
            raise ValueError(
                f"Input and requested output exceed the model context limit "
                f"({self.context_limit} tokens). Shorten the question."
            )
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        with self._generation_lock, torch.inference_mode():
            generated = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                repetition_penalty=self.repetition_penalty,
                no_repeat_ngram_size=self.no_repeat_ngram_size,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        response = self.tokenizer.decode(
            generated[0, input_length:], skip_special_tokens=True
        ).strip()
        if not response:
            raise RuntimeError("The model generated an empty response.")
        return response
