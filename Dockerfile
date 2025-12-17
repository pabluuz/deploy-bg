FROM runpod/base:0.6.0-cuda12.1

WORKDIR /app
COPY . .

# Install both workers' dependencies
RUN pip install --no-cache-dir -r image_worker/requirements.txt \
 && pip install --no-cache-dir -r llm_worker/requirements.txt

# Default command (Runpod endpoint can override this)
CMD ["python", "-u", "image_worker/handler.py"]
