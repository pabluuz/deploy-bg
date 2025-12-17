import os
from typing import Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class LLMService:
    """Minimal Transformers text generation service for Runpod Serverless."""

    def __init__(
        self,
        model_id: str,
        device: Optional[str] = None,
    ):
        self.model_id = model_id

        # Let transformers decide placement if device_map is used.
        # On Runpod GPU, 'auto' will place on GPU when possible.
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=dtype,
            device_map="auto",
            trust_remote_code=True,
        )
        self.model.eval()

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt")

        # When device_map='auto', model can be on multiple devices; move inputs to first device.
        # This is a common pragmatic approach for simple single-GPU setups.
        device = getattr(self.model, "device", None)
        if device is not None:
            inputs = {k: v.to(device) for k, v in inputs.items()}

        do_sample = temperature is not None and float(temperature) > 0

        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=int(max_new_tokens),
                do_sample=do_sample,
                temperature=float(temperature) if do_sample else None,
                top_p=float(top_p) if do_sample else None,
            )

        return self.tokenizer.decode(out[0], skip_special_tokens=True)
