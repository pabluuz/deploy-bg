
from vllm import LLM, SamplingParams

class LLMService:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.llm = LLM(model=model_id)

    def generate(self, prompt: str, max_new_tokens: int = 256, temperature: float = 0.7, top_p: float = 0.9) -> str:
        params = SamplingParams(
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        outputs = self.llm.generate([prompt], params)
        return outputs[0].outputs[0].text.strip()
