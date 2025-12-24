FROM runpod/pytorch:1.0.3-cu1290-torch290-ubuntu2204

WORKDIR /app
COPY . .


ENV XDG_CACHE_HOME=/app/tts_cache
ENV COQUI_TOS_AGREED=1
RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt

# gptqmodel builds from source; during docker build there is usually no GPU/nvidia-smi,
# so force supported architectures explicitly
ENV CUDA_ARCH_LIST="7.5;8.0;8.6;8.9;9.0"
ENV BUILD_CUDA_EXT=1
RUN python -m pip install --no-cache-dir --no-build-isolation gptqmodel

RUN python -c "import runpod; print('runpod import OK')"
RUN python -c "from TTS.api import TTS; TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2', gpu=False)"

CMD ["python", "-u", "handler.py"]
