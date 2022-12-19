FROM python:3.11-slim as base

ARG PROJECT=apis/brand_api

WORKDIR /home/user

# Confirm if pip is updated
RUN pip3 install --upgrade pip

# Install Poetry.
RUN --mount=type=cache,target=/root/.cache pip install poetry==1.3.1
ENV \
    PATH="/home/user/.local/bin:/home/user/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true

COPY ./pyproject.toml ./poetry.lock ./alembic.ini ./
RUN  --mount=type=cache,target=/root/.cache poetry install

FROM base as dev

COPY ./$PROJECT /home/user/$PROJECT

CMD ["uvicorn", "apis.brand_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base as test

RUN --mount=type=cache,target=/root/.cache poetry install --with dev
COPY ./$PROJECT /home/user/$PROJECT
RUN mkdir /home/user/.mypy_cache

# Default target.
FROM dev
