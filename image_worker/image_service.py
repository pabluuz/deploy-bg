import base64
import io
import time
from typing import Optional, Tuple

import torch
from diffusers import AutoPipelineForText2Image
from PIL import Image

DEFAULT_NEGATIVE_PROMPT = (
    "worst quality, low quality, lowres, blurry, jpeg artifacts, noise, "
    "watermark, signature, logo, text, caption, "
    "deformed, disfigured, bad anatomy, malformed, extra limbs, "
    "duplicate, cropped, out of frame, "
    "glitch, tiling, poorly drawn"
)

class ImageGenService:
    """Minimal Diffusers text-to-image service meant for Runpod Serverless.

    - Loads the pipeline once per warm worker (kept in a module-level singleton in handler.py)
    - Generates a PIL.Image and can return it as base64 PNG
    """

    def __init__(
        self,
        model_id: str,
        device: str = "cuda",
        dtype: Optional[torch.dtype] = None,
        disable_progress: bool = True,
    ):
        t0 = time.perf_counter()

        if device != "cuda" or not torch.cuda.is_available():
            raise RuntimeError("CUDA (GPU) is required. Make sure PyTorch sees your GPU.")

        if dtype is None:
            # Sensible default on GPU
            dtype = torch.float16

        self.model_id = model_id
        self.device = device
        self.dtype = dtype

        # Diffusers pipeline
        print("INIT: start", flush=True)
        pipe = AutoPipelineForText2Image.from_pretrained(
            model_id,
            torch_dtype=dtype,
            safety_checker=None,
            requires_safety_checker=False,
        )
        print("INIT: from_pretrained done", flush=True)
        pipe = pipe.to(device)
        
        print("INIT: to(cuda) done", flush=True)

        if disable_progress:
            try:
                pipe.set_progress_bar_config(disable=True)
            except Exception:
                pass

        self.pipe = pipe
        self.init_time_s = time.perf_counter() - t0

    @staticmethod
    def encode_base64_png(img: Image.Image) -> str:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def generate(
        self,
        prompt: str,
        size: int = 512,
        steps: int = 10,
        seed: int = 42,
        guidance_scale: float = 0.0,
        negative_prompt: Optional[str] = None,
    ) -> Tuple[Image.Image, float]:
        """Generate an image and return (PIL.Image, generation_time_seconds)."""
        t0 = time.perf_counter()

        # Deterministic-ish
        generator = torch.Generator(device=self.device).manual_seed(int(seed))

        if negative_prompt is None:
            neg = DEFAULT_NEGATIVE_PROMPT
        else:
            neg = negative_prompt

        out = self.pipe(
            prompt=prompt,
            negative_prompt=neg,
            num_inference_steps=int(steps),
            guidance_scale=float(guidance_scale),
            width=int(size),
            height=int(size),
            generator=generator,
        )

        img = out.images[0]
        return img, (time.perf_counter() - t0)
