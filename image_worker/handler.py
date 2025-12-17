import os
import runpod

from image_service import ImageGenService

_SERVICE = None


def _get_service() -> ImageGenService:
    global _SERVICE
    if _SERVICE is None:
        model_id = os.getenv("IMG_MODEL_ID", "madebyollin/tinysd-1-1b")
        steps_default = int(os.getenv("IMG_STEPS_DEFAULT", "10"))
        size_default = int(os.getenv("IMG_SIZE_DEFAULT", "512"))
        # store defaults on service object for convenience
        svc = ImageGenService(model_id=model_id)
        svc.steps_default = steps_default
        svc.size_default = size_default
        _SERVICE = svc
    return _SERVICE


def handler(job):
    svc = _get_service()
    inp = job.get("input", {}) or {}

    prompt = inp.get("prompt")
    if not prompt:
        return {"error": "Missing required field: input.prompt"}

    steps = int(inp.get("steps", getattr(svc, "steps_default", 10)))
    size = int(inp.get("size", getattr(svc, "size_default", 512)))
    seed = int(inp.get("seed", 42))
    guidance_scale = float(inp.get("guidance_scale", 0.0))

    img, gen_time = svc.generate(
        prompt=prompt,
        steps=steps,
        size=size,
        seed=seed,
        guidance_scale=guidance_scale,
    )
    b64 = svc.encode_base64_png(img)

    return {
        "image_base64": b64,
        "gen_time_s": gen_time,
        "model_init_time_s": svc.init_time_s,
        "model_id": svc.model_id,
        "steps": steps,
        "size": size,
        "seed": seed,
        "guidance_scale": guidance_scale,
    }


runpod.serverless.start({"handler": handler})
