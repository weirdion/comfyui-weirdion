.PHONY: help setup test lint format type-check clean dev-install checks

help:
	@echo "ComfyUI weirdion - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup        - Install dependencies with uv"
	@echo "  make dev-install  - Install in development mode"
	@echo ""
	@echo "Development:"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run ruff linter"
	@echo "  make format       - Format code with ruff"
	@echo "  make type-check   - Run mypy type checking"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make checks       - Run all checks (format, lint, type-check, test)"
	@echo ""

setup:
	uv venv
	uv pip install -e ".[dev]"

dev-install:
	uv pip install -e ".[dev]"

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff check --fix .
	uv run ruff format .

type-check:
	uv run mypy src/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/

checks: format lint type-check test
