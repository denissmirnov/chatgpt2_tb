FROM python:3.11-slim

RUN apt update && apt -y install libpq-dev gcc curl

WORKDIR /app

ENV PYTHONPATH=/app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

CMD python main.py
