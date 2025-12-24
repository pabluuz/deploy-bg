FROM runpod/pytorch:1.0.3-cu1290-torch290-ubuntu2204

WORKDIR /app
COPY . .


ENV XDG_CACHE_HOME=/app/tts_cache
ENV COQUI_TOS_AGREED=1
RUN python -m pip install --upgrade pip && \
	python -m pip install --no-cache-dir -r requirements.txt


RUN python -c "import runpod; print('runpod import OK')"
RUN python -c "from TTS.api import TTS; TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2', gpu=False)"

# Preload SDXL model to HuggingFace cache during build
RUN python -c "from diffusers import StableDiffusionXLPipeline; StableDiffusionXLPipeline.from_pretrained('stabilityai/stable-diffusion-xl-base-1.0', torch_dtype='auto')"

CMD ["python", "-u", "handler.py"]
