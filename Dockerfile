FROM python:3.11-alpine
RUN apk add libpq-dev build-base
COPY hashtablebot hashtablebot
COPY requirements.txt .
RUN pip install -r requirements.txt
