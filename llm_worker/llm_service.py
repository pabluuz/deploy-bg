import os
from typing import Optional


from transformers import AutoTokenizer
from auto_gptq import AutoGPTQForCausalLM


class LLMService:
    """Minimal Transformers text generation service for Runpod Serverless (GPTQ version)."""

    def __init__(self, model_id: str, device: Optional[str] = None):
        self.model_id = model_id
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        self.model = AutoGPTQForCausalLM.from_quantized(
            model_id,
            device="cuda:0",
            use_safetensors=True,
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
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        do_sample = temperature is not None and float(temperature) > 0
        with self.model.device:
            out = self.model.generate(
                **inputs,
                max_new_tokens=int(max_new_tokens),
                do_sample=do_sample,
                temperature=float(temperature) if do_sample else None,
                top_p=float(top_p) if do_sample else None,
            )
        return self.tokenizer.decode(out[0], skip_special_tokens=True)
