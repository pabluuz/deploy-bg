
# Runpod Serverless: Image & LLM API (One Repo)

This repository provides two endpoints for Runpod Serverless, both deployable from a single GitHub repo:

- **Image Generation** (Stable Diffusion via Diffusers)
- **Text Generation** (Transformers LLM)

## Deployment

Deploy using the default `handler.py` entrypoint. Select the endpoint type via the `WORKER` environment variable:

- `WORKER=image` — image generation
- `WORKER=llm` — text generation

**Dockerfile** and `handler.py` are preconfigured for Runpod. Set model IDs and other options via environment variables as needed.

### Example Environment Variables

- For image:
  - `IMG_MODEL_ID=madebyollin/tinysd-1-1b`
  - `IMG_STEPS_DEFAULT=10`
  - `IMG_SIZE_DEFAULT=512`
- For LLM:
  - `LLM_MODEL_ID=qwen/qwen3-8b`
  - `LLM_MAX_NEW_TOKENS_DEFAULT=256`
- (Optional) `HF_HOME=/runpod-volume/hf` for model cache



## API Input/Output

### Autoryzacja

Do każdego żądania należy dodać nagłówek:

    Authorization: Bearer <api_key_here>

### Asynchroniczny workflow (zalecany na Runpod)

1. **Wyślij żądanie POST do endpointa /run:**

       https://api.runpod.ai/v2/<endpoint_id>/run

   W odpowiedzi otrzymasz job ID i status (np. IN_QUEUE).

2. **Sprawdzaj status i odbierz wynik:**

       https://api.runpod.ai/v2/<endpoint_id>/status/<job_id>

   Gdy status będzie COMPLETED, pole `output` zawiera wynik.

### Image Generation
**Input:**
```json
{
  "input": {
    "prompt": "a tiny knight, pixel art",
    "seed": 42,
    "steps": 10,
    "size": 512,
    "guidance_scale": 0.0
  }
}
```
**Odpowiedź z /run:**
```json
{
  "id": "0bb734ce-cd27-471a-801d-55aa4f326241-e2",
  "status": "IN_QUEUE"
}
```
**Odpowiedź z /status/<job_id> (po zakończeniu):**
```json
{
  "delayTime": 11515,
  "executionTime": 47678,
  "id": "0bb734ce-cd27-471a-801d-55aa4f326241-e2",
  "output": {
    "gen_time_s": 4.83,
    "guidance_scale": 7,
    "image_base64": "<base64 PNG>",
    "model_id": "stabilityai/stable-diffusion-xl-base-1.0",
    "model_init_time_s": 42.48,
    "seed": 42,
    "size": 512,
    "steps": 30
  },
  "status": "COMPLETED",
  "workerId": "ilxf2mf5eo0z0k"
}
```

### Text Generation
**Input (z obsługą historii i system_message):**
```json
{
  "input": {
    "system_message": "Jesteś zwięzłym Mistrzem Gry w tekstowej grze fabularnej fantasy. Zachowuj ścisłą ciągłość narracji. W każdej turze zwróć TYLKO jeden zwięzły obiekt JSON (bez markdown, bez dodatkowych znaków), z kluczami: { 'narration': string (6–10 krótkich zdań, maks ~220 słów, 2. osoba, PO POLSKU), 'image_prompt': string (opis jednej sceny do generatora obrazów, po angielsku, max 30 słów; bez tekstu/wodnych znaków) } Bez dodatkowych kluczy. Bez wyjaśnień. Ton: przygodowy, skupiony. Cała gra toczy się w świecie fantasy. Każda narracja musi kończyć się jasną sytuacją, pytaniem lub wyzwaniem dla gracza, zachęcając go do działania lub podjęcia decyzji. Używaj wyłącznie pojedynczych cudzysłowów (') dla wszystkich wartości JSON, nigdy podwójnych (\").",
    "history": [
      {
        "user": "Rozpocznij grę. Chcę wejść do mrocznego lasu.",
        "assistant": "{ 'narration': 'Wchodzisz do mrocznego lasu, gdzie mgła spowija drzewa, a cisza jest niepokojąca. Słyszysz szelest liści pod stopami. Przed tobą ścieżka rozdziela się na dwie odnogi.', 'image_prompt': 'A misty, dark fantasy forest with two diverging paths' }"
      },
      {
        "user": "Idę w lewo i rozglądam się za śladami.",
        "assistant": "{ 'narration': 'Idziesz w lewo, ostrożnie rozglądając się po ściółce. Widzisz świeże ślady butów oraz kilka połamanych gałązek. W oddali słychać cichy szmer wody.', 'image_prompt': 'A fantasy forest path with footprints and broken branches' }"
      }
    ],
    "prompt": "Co widzę na ścieżce? Czy są jakieś ślady lub pułapki?",
    "max_new_tokens": 220,
    "temperature": 0.7,
    "top_p": 0.9
  }
}
```
**Odpowiedź z /run:**
```json
{
  "id": "...",
  "status": "IN_QUEUE"
}
```
**Odpowiedź z /status/<job_id> (po zakończeniu):**
```json
{
  "output": {
    "text": "..."
  },
  "status": "COMPLETED"
}
```

### Text-to-Speech (TTS)

**Input:**
```json
{
  "input": {
    "text": "Witaj świecie w tym pięknym dniu"
  }
}
```
**Odpowiedź z /run:**
```json
{
  "id": "...",
  "status": "IN_QUEUE"
}
```
**Odpowiedź z /status/<job_id> (po zakończeniu):**
```json
{
  "output": {
    "audio_wav_b64": "<base64 WAV>",
    "sample_rate": 24000
  },
  "status": "COMPLETED"
}
```
Plik audio zwracany jest jako base64 zakodowany WAV. Aby odsłuchać, zapisz go do pliku audio.wav:
```python
import base64
b64 = "<base64 WAV>"
with open("audio.wav", "wb") as f:
    f.write(base64.b64decode(b64))
```

## Notes

- For production, consider: streaming for LLM, concurrency limits, timeouts, retry logic, and quantization for lower VRAM use.
