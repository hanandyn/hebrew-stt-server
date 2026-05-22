FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y libsndfile1 curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py ./

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

EXPOSE 8881

CMD ["python", "server.py"]
