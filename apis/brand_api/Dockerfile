FROM python:3.11-slim as base

# define variable
ARG PROJECT=apis/brand_api

# this will be the working directory
WORKDIR /home/user

# If this is set to a non-empty string, Python won’t try to write .pyc files on the import of source modules.
ENV PYTHONDONTWRITEBYTECODE 1

# If this is set to a non-empty string, force the stdout and stderr streams to be unbuffered.
# This option has no effect on the stdin stream.
ENV PYTHONUNBUFFERED 1

# Confirm if pip is updated
RUN pip3 install --upgrade pip

# Install Poetry.
RUN --mount=type=cache,target=/root/.cache pip install poetry==1.3.1

# set environment variables for poetry
ENV PATH="/home/user/.local/bin:/home/user/.venv/bin:${PATH}"
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# copy files needed for poetry install, and run it
COPY ./pyproject.toml ./poetry.lock ./alembic.ini ./
RUN  --mount=type=cache,target=/root/.cache poetry install


#
# dev target
#
FROM base as dev

# copy project
COPY ./$PROJECT /home/user/$PROJECT

# start app with uvicorn
CMD ["uvicorn", "apis.brand_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


#
# test target
#
FROM base as test

# install dev dependecies with poetry
RUN --mount=type=cache,target=/root/.cache poetry install --with dev

# copy project
COPY ./$PROJECT /home/user/$PROJECT

# Creates the directory for the default location where mypy stores incremental cache info.
RUN mkdir /home/user/.mypy_cache


#
# Default target.
#
FROM dev
