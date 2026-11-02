from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from contextlib import nullcontext
from importlib.metadata import version
from pathlib import Path
from typing import Any

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

import numpy as np
import torch
from peft import LoraConfig, get_peft_model
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, get_linear_schedule_with_warmup

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from financial_llm.data.dataset import dataset_sha256  # noqa: E402


class TokenizedDataset(Dataset[dict[str, torch.Tensor]]):
    def __init__(self, path: Path) -> None:
        self.items = json.loads(path.read_text(encoding="utf-8"))
        if not self.items:
            raise ValueError(f"Dataset is empty: {path}")
        for index, item in enumerate(self.items, start=1):
            ids = item.get("input_ids")
            mask = item.get("attention_mask")
            labels = item.get("labels")
            if not isinstance(ids, list) or not ids:
                raise ValueError(f"Record {index} has no input IDs.")
            if not isinstance(mask, list) or len(mask) != len(ids):
                raise ValueError(f"Record {index} has an invalid attention mask.")
            if not isinstance(labels, list) or len(labels) != len(ids):
                raise ValueError(f"Record {index} has invalid labels.")
            if not any(label != -100 for label in labels):
                raise ValueError(f"Record {index} has no supervised response tokens.")
        self.path = path

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        item = self.items[index]
        return {
            key: torch.tensor(item[key], dtype=torch.long)
            for key in ("input_ids", "attention_mask", "labels")
        }


def collate_batch(
    examples: list[dict[str, torch.Tensor]], pad_token_id: int
) -> dict[str, torch.Tensor]:
    maximum = max(item["input_ids"].numel() for item in examples)
    batch: dict[str, list[torch.Tensor]] = {
        "input_ids": [],
        "attention_mask": [],
        "labels": [],
    }
    for item in examples:
        padding = maximum - item["input_ids"].numel()
        batch["input_ids"].append(
            torch.nn.functional.pad(item["input_ids"], (0, padding), value=pad_token_id)
        )
        batch["attention_mask"].append(
            torch.nn.functional.pad(item["attention_mask"], (0, padding), value=0)
        )
        batch["labels"].append(
            torch.nn.functional.pad(item["labels"], (0, padding), value=-100)
        )
    return {key: torch.stack(values) for key, values in batch.items()}


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if hasattr(torch.backends, "cudnn"):
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def optimizer_step_succeeded(previous_scale: float, current_scale: float) -> bool:
    return current_scale >= previous_scale


def load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError(f"Training configuration must be a JSON object: {path}")
    return config


def evaluate_loss(
    model: torch.nn.Module,
    loader: DataLoader[dict[str, torch.Tensor]],
    device: torch.device,
    use_fp16: bool,
) -> tuple[float, int]:
    model.eval()
    total_loss = 0.0
    response_tokens = 0
    with torch.inference_mode():
        for batch in loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            context = (
                torch.autocast(device_type="cuda", dtype=torch.float16)
                if use_fp16
                else nullcontext()
            )
            with context:
                output = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels,
                )
            count = int((labels[:, 1:] != -100).sum().item())
            total_loss += float(output.loss.item()) * count
            response_tokens += count
    if not response_tokens:
        raise ValueError("Validation partition contains no response tokens.")
    model.train()
    return total_loss / response_tokens, response_tokens


def create_model(
    model_name: str,
    family: str,
    family_config: dict[str, Any],
    device: torch.device,
) -> torch.nn.Module:
    model_dtype = (
        torch.float16
        if family == "lora" and device.type == "cuda"
        else torch.float32
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype=model_dtype,
        local_files_only=True,
    )
    if family == "lora":
        model = get_peft_model(
            model,
            LoraConfig(
                r=int(family_config["rank"]),
                lora_alpha=int(family_config["alpha"]),
                target_modules=list(family_config["target_modules"]),
                lora_dropout=float(family_config["dropout"]),
                bias="none",
                task_type="CAUSAL_LM",
                fan_in_fan_out=True,
            ),
        )
        model.enable_input_require_grads()
    model.to(device)
    if family_config.get("gradient_checkpointing", True):
        model.gradient_checkpointing_enable()
    model.config.use_cache = False
    return model


def train(
    family: str,
    config_path: Path,
    tokenized_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    if family not in {"full", "lora"}:
        raise ValueError("family must be 'full' or 'lora'.")
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite experiment directory: {output_dir}")
    config = load_config(config_path)
    family_config = dict(config["full_finetuning" if family == "full" else "lora"])
    seed = int(config["seed"])
    set_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_fp16 = device.type == "cuda" and family_config.get("mixed_precision") == "fp16"

    tokenizer_path = PROJECT_ROOT / "models" / "full_finetuned_gpt2"
    tokenizer = AutoTokenizer.from_pretrained(
        str(tokenizer_path), local_files_only=True
    )
    if tokenizer.eos_token_id is None:
        raise ValueError("GPT-2 tokenizer has no EOS token.")
    tokenizer.pad_token = tokenizer.eos_token

    train_dataset = TokenizedDataset(tokenized_dir / "train.json")
    validation_dataset = TokenizedDataset(tokenized_dir / "validation.json")
    batch_size = int(family_config["batch_size"])
    generator = torch.Generator().manual_seed(seed)
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        generator=generator,
        collate_fn=lambda batch: collate_batch(batch, tokenizer.pad_token_id),
    )
    validation_loader = DataLoader(
        validation_dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=lambda batch: collate_batch(batch, tokenizer.pad_token_id),
    )

    model = create_model(
        str(config["base_model"]), family, family_config, device
    )
    trainable = [parameter for parameter in model.parameters() if parameter.requires_grad]
    if not trainable:
        raise RuntimeError("The selected model has no trainable parameters.")
    optimizer = torch.optim.AdamW(
        trainable,
        lr=float(family_config["learning_rate"]),
        weight_decay=float(family_config.get("weight_decay", 0.0)),
    )
    accumulation = int(family_config["gradient_accumulation_steps"])
    steps_per_epoch = math.ceil(len(train_loader) / accumulation)
    total_steps = steps_per_epoch * int(family_config["epochs"])
    warmup_steps = int(total_steps * float(family_config.get("warmup_ratio", 0)))
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps
    )
    scaler = torch.amp.GradScaler("cuda", enabled=use_fp16)

    output_dir.mkdir(parents=True)
    tokenizer.save_pretrained(output_dir)
    manifest = {
        "family": family,
        "base_model": config["base_model"],
        "offline_mode": True,
        "seed": seed,
        "device": str(device),
        "gpu": torch.cuda.get_device_name(0) if device.type == "cuda" else None,
        "train_examples": len(train_dataset),
        "validation_examples": len(validation_dataset),
        "max_length": config["max_length"],
        "config": family_config,
        "training_config_sha256": dataset_sha256(config_path),
        "train_tokenized_sha256": dataset_sha256(tokenized_dir / "train.json"),
        "validation_tokenized_sha256": dataset_sha256(
            tokenized_dir / "validation.json"
        ),
        "split_metadata_sha256": dataset_sha256(
            tokenized_dir.parent / "split_metadata.json"
        ),
        "python_version": sys.version,
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "transformers_version": version("transformers"),
        "peft_version": version("peft"),
        "numpy_version": np.__version__,
    }
    (output_dir / "training_config.json").write_text(
        json.dumps(config, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "experiment.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    records: list[dict[str, float | int]] = []
    model.train()
    optimizer.zero_grad(set_to_none=True)
    for epoch in range(int(family_config["epochs"])):
        epoch_token_loss = 0.0
        epoch_response_tokens = 0
        examples_seen = 0
        optimizer_steps = 0
        skipped_optimizer_steps = 0
        accumulated = 0
        for step, batch in enumerate(train_loader):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            context = (
                torch.autocast(device_type="cuda", dtype=torch.float16)
                if use_fp16
                else nullcontext()
            )
            with context:
                output = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels,
                )
                loss = output.loss
            batch_response_tokens = int((labels[:, 1:] != -100).sum().item())
            epoch_token_loss += float(loss.item()) * batch_response_tokens
            epoch_response_tokens += batch_response_tokens
            examples_seen += input_ids.shape[0]
            remaining = len(train_loader) - step
            window_size = min(accumulation, remaining + accumulated)
            scaler.scale(loss / window_size).backward()
            accumulated += 1
            if accumulated == accumulation or step + 1 == len(train_loader):
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(
                    trainable, float(family_config["gradient_clip_norm"])
                )
                previous_scale = scaler.get_scale()
                scaler.step(optimizer)
                scaler.update()
                if optimizer_step_succeeded(previous_scale, scaler.get_scale()):
                    scheduler.step()
                    optimizer_steps += 1
                else:
                    skipped_optimizer_steps += 1
                optimizer.zero_grad(set_to_none=True)
                accumulated = 0

        validation_loss, validation_tokens = evaluate_loss(
            model, validation_loader, device, use_fp16
        )
        record = {
            "epoch": epoch + 1,
            "train_loss_per_response_token": (
                epoch_token_loss / epoch_response_tokens
                if epoch_response_tokens
                else None
            ),
            "validation_loss_per_response_token": validation_loss,
            "validation_perplexity": math.exp(validation_loss),
            "validation_response_tokens": validation_tokens,
            "examples_seen": examples_seen,
            "optimizer_steps": optimizer_steps,
            "skipped_optimizer_steps": skipped_optimizer_steps,
        }
        records.append(record)
        checkpoint = output_dir / f"checkpoint-epoch-{epoch + 1}"
        model.save_pretrained(checkpoint)
        tokenizer.save_pretrained(checkpoint)
        print(json.dumps(record))

    model.config.use_cache = True
    final_dir = output_dir / "final"
    model.save_pretrained(final_dir)
    tokenizer.save_pretrained(final_dir)
    (output_dir / "metrics.json").write_text(
        json.dumps(records, indent=2) + "\n", encoding="utf-8"
    )
    return {"manifest": manifest, "metrics": records}


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune GPT-2 locally.")
    parser.add_argument("--family", choices=("full", "lora"), required=True)
    parser.add_argument(
        "--config", type=Path, default=PROJECT_ROOT / "configs" / "training.json"
    )
    parser.add_argument(
        "--tokenized-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "tokenized",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    train(args.family, args.config, args.tokenized_dir, args.output_dir)


if __name__ == "__main__":
    main()
