# Runpod Serverless: Two Endpoints (Image + LLM)

This repo is meant to be deployed on **Runpod Serverless** as **two separate endpoints** from the same GitHub repository:

- **Image endpoint** (`image_worker/handler.py`): Stable Diffusion via Diffusers (default: `madebyollin/tinysd-1-1b`)
- **LLM endpoint** (`llm_worker/handler.py`): Transformers text generation (default: `qwen/qwen3-8b`)

## 1) Deploy on Runpod (two endpoints, one repo)

Create two Serverless Endpoints pointing to this repo:

### Endpoint A — Image
- **Start Command**: `python -u image_worker/handler.py`
- **Env** (recommended):
  - `IMG_MODEL_ID=madebyollin/tinysd-1-1b`
  - `IMG_STEPS_DEFAULT=10`
  - `IMG_SIZE_DEFAULT=512`
  - `HF_HOME=/runpod-volume/hf` (optional, improves caching if you mount a volume)

### Endpoint B — LLM
- **Start Command**: `python -u llm_worker/handler.py`
- **Env** (recommended):
  - `LLM_MODEL_ID=qwen/qwen3-8b`
  - `LLM_MAX_NEW_TOKENS_DEFAULT=256`
  - `HF_HOME=/runpod-volume/hf` (optional)

> Tip: If you mount a Runpod Volume and set `HF_HOME`, model downloads are cached across restarts and cold starts are much less painful.

## 2) Request format

### Image endpoint input
```json
{
  "input": {
    "prompt": "a tiny knight, pixel art",
    "seed": 42,
    "steps": 10,
    "size": 512,
    "guidance_scale": 0.0
  }
}
```

Returns:
```json
{
  "image_base64": "<base64 PNG>",
  "gen_time_s": 1.23,
  "model_init_time_s": 2.34
}
```

### LLM endpoint input
```json
{
  "input": {
    "prompt": "Write a short poem about rain.",
    "max_new_tokens": 200,
    "temperature": 0.7,
    "top_p": 0.9
  }
}
```

Returns:
```json
{
  "text": "..."
}
```

## 3) Notes

- This repo is a **starting point**. For production you probably want:
  - streaming for LLM,
  - concurrency limits,
  - timeouts + retry logic on the caller side,
  - quantization (4-bit) to reduce VRAM.
