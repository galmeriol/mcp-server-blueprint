.DEFAULT_GOAL := help

.PHONY: help install lint format typecheck test audit check serve

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

install: ## Install all dependencies (including dev)
	uv sync

lint: ## Check code style and lint rules (ruff)
	uv run ruff check src/ tests/

format: ## Auto-format and fix lint violations (ruff)
	uv run ruff check --fix src/ tests/
	uv run ruff format src/ tests/

typecheck: ## Run static type checking (ty)
	uv run ty check src/

test: ## Run tests with coverage report
	uv run pytest

audit: ## Scan dependencies for known vulnerabilities (pip-audit)
	uv run pip-audit --skip-editable

check: lint typecheck test audit ## Run all static checks, tests, and security audit

serve: ## Start the MCP server locally (http://127.0.0.1:8000/mcp)
	uv run mcp-server-blueprint
