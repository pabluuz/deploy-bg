FROM runpod/base:0.6.2-cuda12.1.0

WORKDIR /app
COPY . .

# Install both workers' dependencies
RUN pip install --no-cache-dir -r image_worker/requirements.txt \
 && pip install --no-cache-dir -r llm_worker/requirements.txt

# Default command (Runpod endpoint can override this)
ARG WORKER=image
CMD ["python", "-u", "-m", "${WORKER}_worker.handler"]
