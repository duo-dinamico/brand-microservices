SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

# export DOCKER_BUILDKIT=1
# export COMPOSE_DOCKER_CLI_BUILD=1
export PROJECT=apis/brand_api

targets: help

ci-docker-compose := docker compose -f .ci/docker-compose.yml

up: ## Run the application
	docker compose up --build brand_api

build: ## Build the docker image
	docker compose build

buildci: ## Build the ci image
	$(ci-docker-compose) build

down: ## Stop the application
	docker compose down

downci:  ## Clean up test containers
	$(ci-docker-compose) down

# done: lint ## Prepare for a commit

test: utest itest  ## Run unit and integration tests

utest: ## Run unit tests
	$(ci-docker-compose) run --rm unit pytest-watch ./apis/brand_api/tests

itest: ## Run integration tests
	$(ci-docker-compose) run --rm integration pytest-watch ./apis/brand_api/tests

check: ## Check the code base
	poetry run black ./$(PROJECT) --check --diff
	poetry run unit isort ./$(PROJECT) --check --diff
	poetry run mypy ./$(PROJECT)

lint: ## Check the code base, and fix it
	poetry run black ./$(PROJECT)
	poetry run isort ./$(PROJECT)
	poetry run mypy ./$(PROJECT)

## Migrations

migrations: ## Generate a migration using alembic
ifeq ($(m),)
	@echo "Specify a message with m={message} and a rev-id with revid={revid} (e.g. 0001 etc.)"; exit 1
else ifeq ($(revid),)
	@echo "Specify a message with m={message} and a rev-id with revid={revid} (e.g. 0001 etc.)"; exit 1
else
	docker compose run brand_api alembic revision --autogenerate -m "$(m)" --rev-id="$(revid)"
endif

migrate: ## Run migrations upgrade using alembic
	docker compose run --rm brand_api alembic upgrade head

downgrade: ## Run migrations downgrade using alembic
	docker compose run --rm brand_api alembic downgrade -1

help: ## Display this help message
	@awk -F '##' '/^[a-z_]+:[a-z ]+##/ { print "\033[34m"$$1"\033[0m" "\n" $$2 }' Makefile
