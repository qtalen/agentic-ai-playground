FROM python:3.13-slim

WORKDIR /workspace

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
