FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y libsndfile1 curl git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the model at build time
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('ivrit-ai/whisper-large-v3-turbo-ct2', download_root='/app/models')"

COPY server.py ./

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

EXPOSE 8881

CMD ["python", "server.py"]
