FROM python:3.10.3-slim-buster as os-base
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
RUN apt-get update
RUN apt-get install -y curl

FROM os-base as poetry-base

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH="/root/.poetry/bin:$PATH"
RUN poetry config virtualenvs.create false
RUN apt-get remove -y curl

FROM poetry-base as app-base

WORKDIR /backend
ADD . /backend
COPY pyproject.toml ./pyproject.toml
RUN poetry install

FROM app-base as main

CMD tail -f /dev/null