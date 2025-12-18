FROM runpod/pytorch:1.0.3-cu1290-torch290-ubuntu2204

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r image_worker/requirements.txt \
 && pip install --no-cache-dir -r llm_worker/requirements.txt

RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]
