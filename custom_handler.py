# custom_handler.py
import os
import runpod

WORKER = os.getenv("WORKER", "").lower()

if WORKER == "image":
    from image_worker.handler import handler
elif WORKER == "llm":
    from llm_worker.handler import handler
else:
    raise RuntimeError(
        "Invalid WORKER env. Expected WORKER=image or WORKER=llm"
    )

runpod.serverless.start({
    "handler": handler
})
