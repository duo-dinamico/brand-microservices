SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

# export DOCKER_BUILDKIT=1
# export COMPOSE_DOCKER_CLI_BUILD=1
export PROJECT=apis/brand_api

targets: help

docker-compose := docker compose
volume-remove := docker volume rm brand_microservices_psql_db || true
all-dockers := $$(docker ps -a -q)
pt-watch := ENVIRONMENT=test $(docker-compose) -f docker-compose.test.yaml run --rm ci pytest-watch

up: down ## Run the application
	ENVIRONMENT=development $(docker-compose) -f docker-compose.dev.yaml up --build brand_api_development

up-prod: ## Run the application in production
	ENVIRONMENT=production $(docker-compose) -f docker-compose.prod.yaml up -d --build brand_api_production traefik

down: ## Stop the application
	docker stop $(all-dockers) && docker rm $(all-dockers) && $(volume-remove)

test: down ## Run all tests
	$(pt-watch) .

utest: down ## Run user tests
	$(pt-watch) -- -m user .

btest: down ## Run brand tests
	$(pt-watch) -- -m brand .

ctest: down ## Run categories tests
	$(pt-watch) -- -m categories .

atest: down ## Run app tests
	$(pt-watch) -- -m app .

citest: ## Run ci tests
	ENVIRONMENT=test $(docker-compose) -f docker-compose.test.yaml run --rm ci pytest ./apis/brand_api/tests

check: ## Check the code base
	poetry run black ./$(PROJECT) --check --diff --color
	poetry run isort ./$(PROJECT)

lint: ## Check the code base, and fix it
	poetry run black ./$(PROJECT)
	poetry run isort ./$(PROJECT)

## Migrations

migrations: ## Generate a migration using alembic
ifeq ($(m),)
	@echo "Specify a message with m={message} and a rev-id with revid={revid} (e.g. 0001 etc.)"; exit 1
else ifeq ($(revid),)
	@echo "Specify a message with m={message} and a rev-id with revid={revid} (e.g. 0001 etc.)"; exit 1
else
	ENVIRONMENT=development $(docker-compose) -f docker-compose.dev.yaml run brand_api_development alembic revision --autogenerate -m "$(m)" --rev-id="$(revid)"
endif

migrate: down ## Run migrations upgrade using alembic
	ENVIRONMENT=development $(docker-compose) -f docker-compose.dev.yaml run --rm brand_api_development alembic upgrade head

downgrade: down ## Run migrations downgrade using alembic
	ENVIRONMENT=development $(docker-compose) -f docker-compose.dev.yaml run --rm brand_api_development alembic downgrade -1

help: ## Display this help message
	@awk -F '##' '/^[a-z_]+:[a-z ]+##/ { print "\033[34m"$$1"\033[0m" "\n" $$2 }' Makefile
