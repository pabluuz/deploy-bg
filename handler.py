# custom_handler.py
import os
import runpod

WORKER = os.getenv("WORKER", "").lower()

if WORKER == "image":
    from image_worker.image_handler import handler
elif WORKER == "llm":
    from llm_worker.llm_handler import handler
elif WORKER == "tts":
    from tts_worker.tts_handler import handler
else:
    raise RuntimeError(
        "Invalid WORKER env. Expected WORKER=image or WORKER=llm"
    )

runpod.serverless.start({
    "handler": handler
})
