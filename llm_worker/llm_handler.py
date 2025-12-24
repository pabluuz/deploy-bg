import os
import runpod

from llm_worker.llm_service import LLMService

_SERVICE = None


def _get_service() -> LLMService:
    global _SERVICE
    if _SERVICE is None:
        model_id = os.getenv("LLM_MODEL_ID", "teknium/OpenHermes-2.5-Mistral-7B")
        _SERVICE = LLMService(model_id=model_id)
    return _SERVICE


def handler(job):
    svc = _get_service()
    inp = job.get("input", {}) or {}

    prompt = inp.get("prompt")
    if not prompt:
        return {"error": "Missing required field: input.prompt"}

    # Możliwość podania własnego system_message przez input lub ENV
    system_message = inp.get("system_message") or os.getenv("LLM_SYSTEM_MESSAGE") or "Jesteś pomocnym asystentem."


    # Obsługa historii jako lista obiektów z kluczami 'user' i 'assistant'
    history = inp.get("history", [])
    history_blocks = ""
    for turn in history:
        user_msg = turn.get("user")
        assistant_msg = turn.get("assistant")
        if user_msg:
            history_blocks += f"<|im_start|>user\n{user_msg}<|im_end|>\n"
        if assistant_msg:
            history_blocks += f"<|im_start|>assistant\n{assistant_msg}<|im_end|>\n"

    # Template zgodny z formatem chat Mistral/OpenHermes
    prompt_template = (
        "<|im_start|>system\n{system_message}<|im_end|>\n"
        "{history_blocks}"
        "<|im_start|>user\n{prompt}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )
    formatted_prompt = prompt_template.format(system_message=system_message, history_blocks=history_blocks, prompt=prompt)

    max_new = int(inp.get("max_new_tokens", os.getenv("LLM_MAX_NEW_TOKENS_DEFAULT", "256")))
    temperature = float(inp.get("temperature", 0.7))
    top_p = float(inp.get("top_p", 0.9))

    text = svc.generate(
        prompt=formatted_prompt,
        max_new_tokens=max_new,
        temperature=temperature,
        top_p=top_p,
    )
    return {"text": text, "model_id": svc.model_id}
