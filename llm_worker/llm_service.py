import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class LLMService:
    def __init__(self, model_id: str, device: str | None = None):
        self.model_id = model_id
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

        # ważne: GPTQ działa przez integrację transformers+optimum+gptqmodel
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="cuda:0",     # albo "auto"
            torch_dtype="auto",
            trust_remote_code=True,
        )
        self.model.eval()

    def generate(self, prompt: str, max_new_tokens: int = 256, temperature: float = 0.7, top_p: float = 0.9) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        do_sample = temperature is not None and float(temperature) > 0

        with torch.inference_mode():
            out = self.model.generate(
                **inputs,
                max_new_tokens=int(max_new_tokens),
                do_sample=do_sample,
                temperature=float(temperature) if do_sample else None,
                top_p=float(top_p) if do_sample else None,
            )
        return self.tokenizer.decode(out[0], skip_special_tokens=True)
