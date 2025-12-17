FROM runpod/pytorch:2.1.2-py3.10-cuda12.1.1-devel-ubuntu22.04

WORKDIR /app
COPY . .

RUN which python || true && which python3 || true && python3 --version || true

# Install both workers' dependencies
RUN pip install --no-cache-dir -r image_worker/requirements.txt \
 && pip install --no-cache-dir -r llm_worker/requirements.txt

# Default command (Runpod endpoint can override this)
ENV WORKER=image
CMD python3 -u -m "${WORKER}_worker.handler"

