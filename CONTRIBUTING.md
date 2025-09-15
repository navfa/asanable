# Contributing to asanable

Thanks for your interest in contributing!

## Getting Started

```bash
git clone https://github.com/navfa/asanable.git && cd asanable
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Development Workflow

```bash
# Lint and format
make lint
make format

# Run tests
make test

# Run tests with coverage (80% minimum)
make cov

# Verify everything before pushing
make check && make test
```

## Pull Requests

1. Fork the repo and create a branch from `master`
2. Branch naming: `feat/description`, `fix/description`, `refactor/description`
3. Write tests for new functionality
4. Ensure `make check` and `make test` pass
5. Use conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`
6. Keep PRs small and focused — one feature or fix per PR

## Code Style

- Python 3.12+
- Ruff for linting and formatting (configured in `pyproject.toml`)
- Type hints on all function signatures
- Small functions, single responsibility
- Constants and enums instead of magic strings

## Architecture

```
CLI (main.py) → Services → Clients (Asana API)
                    ↑
               Domain (pure dataclasses)
                    ↓
              Renderers (CLI, HTML, Slack, Telegram)
```

- `domain/` — pure dataclasses, no external dependencies
- `clients/` — API wrappers, return domain entities
- `services/` — business logic, no SDK imports
- `renderers/` — output only, no business logic
- `infrastructure/` — cache, clock, technical details

## Good First Issues

Look for issues labeled `good first issue` on GitHub. Some ideas:

- Add `-o json` output format
- Add `--this-week` section filter
- Improve test coverage on `main.py`
- Add a `Dockerfile` for containerized usage

## Questions?

Open an issue on GitHub.
