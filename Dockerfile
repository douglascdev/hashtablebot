FROM python:3.11-alpine
WORKDIR /hashtablebot
ARG channels
ARG token
ENV CHANNELS=${channels}
ENV TOKEN=${token}
ENV LOG_LEVEL=INFO
ENV PYTHONPATH=/hashtablebot
ENV PYTHONUNBUFFERED=1
COPY hashtablebot hashtablebot
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD python3 hashtablebot/main.py 1> bot_output 2> bot_errors
