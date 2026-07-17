FROM python:3.9-slim

# Instala o ffmpeg e dependências de áudio no sistema
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

# O Render exige que a API use a porta dinâmica enviada pela variável $PORT do sistema
CMD uvicorn app:app --host 0.0.0.0 --port $PORT
