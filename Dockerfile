FROM python:3.11-alpine
RUN apk add libpq-dev build-base
ENV PYTHONPATH=/hashtablebot
ENV PYTHONUNBUFFERED=1
COPY hashtablebot hashtablebot
COPY requirements.txt .
RUN pip install -r requirements.txt
