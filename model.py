import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig


def get_chat_model():
    """Initializes and returns the ChatOpenAI model."""

    model_id = "meta-llama/Llama-3.2-3B-Instruct" # Or other Llama 3 models
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    # Load model directly without Pipeline
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )
    return model