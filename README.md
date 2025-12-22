
# Runpod Serverless: Image & LLM API (One Repo)

This repository provides two endpoints for Runpod Serverless, both deployable from a single GitHub repo:

- **Image Generation** (Stable Diffusion via Diffusers)
- **Text Generation** (Transformers LLM)

## Deployment

Deploy using the default `handler.py` entrypoint. Select the endpoint type via the `WORKER` environment variable:

- `WORKER=image` — image generation
- `WORKER=llm` — text generation

**Dockerfile** and `handler.py` are preconfigured for Runpod. Set model IDs and other options via environment variables as needed.

### Example Environment Variables

- For image:
  - `IMG_MODEL_ID=madebyollin/tinysd-1-1b`
  - `IMG_STEPS_DEFAULT=10`
  - `IMG_SIZE_DEFAULT=512`
- For LLM:
  - `LLM_MODEL_ID=qwen/qwen3-8b`
  - `LLM_MAX_NEW_TOKENS_DEFAULT=256`
- (Optional) `HF_HOME=/runpod-volume/hf` for model cache



## API Input/Output

### Autoryzacja

Do każdego żądania należy dodać nagłówek:

    Authorization: Bearer <api_key_here>

### Asynchroniczny workflow (zalecany na Runpod)

1. **Wyślij żądanie POST do endpointa /run:**

       https://api.runpod.ai/v2/<endpoint_id>/run

   W odpowiedzi otrzymasz job ID i status (np. IN_QUEUE).

2. **Sprawdzaj status i odbierz wynik:**

       https://api.runpod.ai/v2/<endpoint_id>/status/<job_id>

   Gdy status będzie COMPLETED, pole `output` zawiera wynik.

### Image Generation
**Input:**
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
**Odpowiedź z /run:**
```json
{
  "id": "0bb734ce-cd27-471a-801d-55aa4f326241-e2",
  "status": "IN_QUEUE"
}
```
**Odpowiedź z /status/<job_id> (po zakończeniu):**
```json
{
  "delayTime": 11515,
  "executionTime": 47678,
  "id": "0bb734ce-cd27-471a-801d-55aa4f326241-e2",
  "output": {
    "gen_time_s": 4.83,
    "guidance_scale": 7,
    "image_base64": "<base64 PNG>",
    "model_id": "stabilityai/stable-diffusion-xl-base-1.0",
    "model_init_time_s": 42.48,
    "seed": 42,
    "size": 512,
    "steps": 30
  },
  "status": "COMPLETED",
  "workerId": "ilxf2mf5eo0z0k"
}
```

### Text Generation
**Input:**
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
**Odpowiedź z /run:**
```json
{
  "id": "...",
  "status": "IN_QUEUE"
}
```
**Odpowiedź z /status/<job_id> (po zakończeniu):**
```json
{
  "output": {
    "text": "..."
  },
  "status": "COMPLETED"
}
```

## Notes

- For production, consider: streaming for LLM, concurrency limits, timeouts, retry logic, and quantization for lower VRAM use.
