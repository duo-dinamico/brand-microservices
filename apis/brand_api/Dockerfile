FROM python:3.11-slim as build

# define variable. Only usable during building, not when start execution.
ENV PIP_DEFAULT_TIMEOUT=100 \
    # Allow statements and log messages to immediately appear
    PYTHONUNBUFFERED=1 \
    # disable a pip version check to reduce run-time & log-spam
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # cache is useless in docker image, so disable to reduce image size
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.3.2 \
    PROJECT=apis/brand_api

# this will be the working directory
WORKDIR /home/user
# copy files needed for poetry install
COPY pyproject.toml poetry.lock ./alembic.ini ./

RUN pip install "poetry==$POETRY_VERSION" \
    && poetry install --no-root --no-ansi --no-interaction \
    && poetry export --with dev -f requirements.txt -o requirements.txt

FROM python:3.11-slim as base

# this will be the working directory
WORKDIR /home/user

COPY --from=build /home/user/requirements.txt .

RUN set -ex \
    # Create a non-root user
    && addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --gid 1001 --no-create-home appuser \
    # Upgrade the package index and install security upgrades
    && apt-get update \
    && apt-get upgrade -y \
    # Install dependencies
    && pip install -r requirements.txt \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

#
# dev target
#
FROM base as dev

# copy project
COPY ./$PROJECT /home/user/$PROJECT

# start app with uvicorn
CMD ["uvicorn", "apis.brand_api.main:app", "--log-config", "apis/brand_api/utils/log.ini", "--host", "0.0.0.0", "--port", "8000", "--reload"]

#
# prod target
#
FROM base as prod

# copy project
COPY ./$PROJECT /home/user/$PROJECT

# start app with uvicorn
CMD ["uvicorn", "apis.brand_api.main:app", "--log-config", "apis/brand_api/utils/log.ini", "--host", "0.0.0.0", "--port", "80"]

USER appuser

#
# test target
#
FROM base as test

# copy project
COPY ./$PROJECT /home/user/$PROJECT

#
# Default target.
#
FROM dev
