FROM python:3.9-slim-buster
WORKDIR /backend
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
ADD . /backend