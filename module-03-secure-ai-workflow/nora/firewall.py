"""Prompt firewall: Meta Llama Prompt Guard 2 (22M), a small classifier that runs on CPU.
Gated model: accept the Llama license on Hugging Face, then `uv run hf auth login`."""
import re

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL_ID = "meta-llama/Llama-Prompt-Guard-2-22M"
THRESHOLD = 0.5

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)


def injection_score(text: str) -> float:
    """Probability that the text tries to override the model's instructions (class 1 = malicious).
    Scored sentence by sentence: an injection buried in normal text is diluted when scored as a whole."""
    sentences = [s for s in re.split(r"(?<=[.!?:])\s+|\n+", text) if s.strip()] or [text]
    inputs = tokenizer(sentences, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        logits = model(**inputs).logits
    return logits.softmax(dim=-1)[:, 1].max().item()
