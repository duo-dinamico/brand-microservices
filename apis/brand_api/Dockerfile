FROM python:3.11-slim as base

ARG PROJECT=apis/brand_api

WORKDIR /home/user

# Install Poetry.
RUN --mount=type=cache,target=/root/.cache pip install poetry==1.2.0
ENV \
    PATH="/home/user/.local/bin:/home/user/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true

COPY ./pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache poetry install

FROM base as dev

COPY ./$PROJECT /home/user/$PROJECT

CMD ["uvicorn", "apis.brand_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Default target.
FROM dev