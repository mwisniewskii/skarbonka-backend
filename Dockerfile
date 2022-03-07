FROM python:3.8-slim-buster
WORKDIR /backend
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
ADD . /backend