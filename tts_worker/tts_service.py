# tts_worker/tts_service.py

import os
os.environ["XDG_CACHE_HOME"] = "/app/tts_cache"
import io
from typing import Optional, Tuple

import numpy as np
import soundfile as sf
import torch
from TTS.api import TTS


class XTTSService:
    """
    XTTS-v2 service for RunPod Serverless with a fixed, packaged voice reference WAV.

    Notes:
    - We intentionally avoid accepting user-provided reference audio to keep the API simple.
    - The handler should only pass `text` (and optionally `language`).
    """

    def __init__(
        self,
        model_id: str = "tts_models/multilingual/multi-dataset/xtts_v2",
        language_default: str = "pl",
        reference_wav_filename: str = "voice_ref.wav",
        device: Optional[str] = None,
    ):
        self.model_id = model_id
        self.language_default = language_default

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device

        # Resolve absolute path to packaged reference wav
        base_dir = os.path.dirname(__file__)
        self.reference_wav_path = os.path.abspath(os.path.join(base_dir, reference_wav_filename))
        if not os.path.exists(self.reference_wav_path):
            raise FileNotFoundError(
                f"Reference WAV not found at: {self.reference_wav_path}. "
                f"Place '{reference_wav_filename}' next to this file in tts_worker/."
            )

        # Initialize Coqui TTS (downloads model into cache on first run)
        self.tts = TTS(model_name=self.model_id, gpu=(self.device == "cuda"))

        # Best-effort output sample rate
        self.sample_rate = (
            getattr(getattr(self.tts, "synthesizer", None), "output_sample_rate", None) or 24000
        )

    def synthesize_wav_bytes(self, text: str, language: Optional[str] = None) -> Tuple[bytes, int]:
        """
        Synthesize speech to WAV bytes using packaged reference voice sample.

        Returns: (wav_bytes, sample_rate)
        """
        if not text or not isinstance(text, str):
            raise ValueError("text must be a non-empty string")

        lang = (language or self.language_default or "pl").strip()

        # Coqui XTTSv2 synthesis
        wav = self.tts.tts(
            text=text,
            speaker_wav=self.reference_wav_path,
            language=lang,
        )

        wav_np = np.asarray(wav, dtype=np.float32)

        buf = io.BytesIO()
        sf.write(buf, wav_np, int(self.sample_rate), format="WAV")
        return buf.getvalue(), int(self.sample_rate)
