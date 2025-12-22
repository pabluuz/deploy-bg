FROM runpod/pytorch:1.0.3-cu1290-torch290-ubuntu2204

WORKDIR /app
COPY . .

RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt

RUN python -c "import runpod; print('runpod import OK')"

CMD ["python", "-u", "handler.py"]
