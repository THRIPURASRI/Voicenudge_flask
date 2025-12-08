FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git ffmpeg libsndfile1 sox libsox-dev libsox-fmt-all \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir torch==2.4.0 torchaudio==2.4.0 torchcodec==0.1.1 soundfile

RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8888
CMD ["gunicorn", "-b", "0.0.0.0:8888", "wsgi:app"]
