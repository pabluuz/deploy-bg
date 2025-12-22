# tts_worker/tts_handler.py
import base64
import os

from tts_worker.tts_service import XTTSService

_SERVICE = None


def _get_service() -> XTTSService:
    global _SERVICE
    if _SERVICE is None:
        # Coqui XTTSv2 model id:
        # Common canonical name:
        #   tts_models/multilingual/multi-dataset/xtts_v2
        model_id = os.getenv("TTS_MODEL_ID", "tts_models/multilingual/multi-dataset/xtts_v2")
        _SERVICE = XTTSService(model_id=model_id)
    return _SERVICE


def handler(job):
    svc = _get_service()
    inp = job.get("input", {}) or {}

    text = inp.get("text")
    if not text:
        return {"error": "Missing required field: input.text"}

    # Polish default
    language = inp.get("language", os.getenv("TTS_LANGUAGE_DEFAULT", "pl"))

    try:
        wav_bytes, sr = svc.synthesize_wav_bytes(
            text=text,
            language=language
        )
    except Exception as e:
        return {"error": f"TTS synthesis failed: {type(e).__name__}: {e}"}

    return {
        "audio_wav_b64": base64.b64encode(wav_bytes).decode("ascii"),
        "sample_rate": sr,
        "model_id": svc.model_id,
        "language": language,
    }
