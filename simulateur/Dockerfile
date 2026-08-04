# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --system --create-home solida
RUN mkdir -p /app/sorties && chown -R solida:solida /app
USER solida

WORKDIR /app/simulateur
CMD ["sh", "-c", "python pipeline.py && python charger_postgres.py"]
