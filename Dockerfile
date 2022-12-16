FROM python:3.11-alpine
ENV PYTHONPATH=/hashtablebot
ENV PYTHONUNBUFFERED=1
COPY hashtablebot hashtablebot
COPY requirements.txt .
RUN pip install -r requirements.txt
