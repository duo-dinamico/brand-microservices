SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

# export DOCKER_BUILDKIT=1
# export COMPOSE_DOCKER_CLI_BUILD=1
export PROJECT=apis/brand_api

targets: help

up: ## Run the application
	docker compose up --build brand_api

down: ## Stop the application
	docker compose down

done: lint ## Prepare for a commit
# test: utest itest  ## Run unit and integration tests

ci-docker-compose := docker compose -f .ci/docker-compose.yml

utest: ## Run unit tests
	$(ci-docker-compose) run --rm unit pytest -m unit .

itest: ## Run integration tests
	$(ci-docker-compose) run --rm integration pytest -m integration .

# check: ## Check the code base
# 	$(ci-docker-compose) run --rm unit black ./$(PROJECT) --check --diff
# 	$(ci-docker-compose) run --rm unit isort ./$(PROJECT) --check --diff
# 	$(ci-docker-compose) run --rm -v mypycache:/home/user/.mypy_cache unit mypy ./$(PROJECT)

lint: ## Check the code base, and fix it
	poetry run black ./$(PROJECT)
	poetry run isort ./$(PROJECT)
	poetry run mypy ./$(PROJECT)

cleantest:  ## Clean up test containers
	$(ci-docker-compose) down


# ## Migrations

# migrations: ## Generate a migration using alembic
# ifeq ($(m),)
# 	@echo "Specify a message with m={message} and a rev-id with revid={revid} (e.g. 0001 etc.)"; exit 1
# else ifeq ($(revid),)
# 	@echo "Specify a message with m={message} and a rev-id with revid={revid} (e.g. 0001 etc.)"; exit 1
# else
# 	docker-compose run api alembic revision --autogenerate -m "$(m)" --rev-id="$(revid)"
# endif

# migrate: ## Run migrations upgrade using alembic
# 	docker-compose run --rm api alembic upgrade head

# downgrade: ## Run migrations downgrade using alembic
# 	docker-compose run --rm api alembic downgrade -1

help: ## Display this help message
	@awk -F '##' '/^[a-z_]+:[a-z ]+##/ { print "\033[34m"$$1"\033[0m" "\n" $$2 }' Makefile
