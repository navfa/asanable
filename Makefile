.DEFAULT_GOAL := help

.PHONY: help install lint format test cov run quiet schedule clean project

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Install project with dev dependencies
	pip install -e ".[dev]"

lint: ## Run linter
	ruff check src/ tests/ --fix

format: ## Format code
	ruff format src/ tests/

check: ## Lint + format check (CI mode, no fix)
	ruff check src/ tests/
	ruff format --check src/ tests/

test: ## Run all tests
	pytest

cov: ## Run tests with coverage report
	pytest --cov=asanable --cov-report=term-missing --cov-fail-under=80

run: ## Run the digest
	python -m asanable

quiet: ## Run digest in quiet mode
	python -m asanable --quiet

project: ## Filter by project (usage: make project P="Mobile App")
	python -m asanable --project "$(P)"

schedule: ## Start the daily scheduler
	python -m asanable --schedule

clean: ## Remove build artifacts and caches
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov dist build src/*.egg-info
