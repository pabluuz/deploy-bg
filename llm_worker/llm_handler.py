import os
import runpod

from llm_worker.llm_service import LLMService

_SERVICE = None


def _get_service() -> LLMService:
    global _SERVICE
    if _SERVICE is None:
        model_id = os.getenv("LLM_MODEL_ID", "qwen/qwen3-8b")
        _SERVICE = LLMService(model_id=model_id)
    return _SERVICE


def handler(job):
    svc = _get_service()
    inp = job.get("input", {}) or {}

    prompt = inp.get("prompt")
    if not prompt:
        return {"error": "Missing required field: input.prompt"}

    max_new = int(inp.get("max_new_tokens", os.getenv("LLM_MAX_NEW_TOKENS_DEFAULT", "256")))
    temperature = float(inp.get("temperature", 0.7))
    top_p = float(inp.get("top_p", 0.9))

    text = svc.generate(
        prompt=prompt,
        max_new_tokens=max_new,
        temperature=temperature,
        top_p=top_p,
    )
    return {"text": text, "model_id": svc.model_id}
