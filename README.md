# asanable

Asana + Gmail daily digest CLI aggregator.

Aggregate your assigned Asana tasks and Gmail notifications into a single, prioritized daily digest.

## Setup

```bash
git clone https://github.com/your-org/asanable.git && cd asanable
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Edit `.env` with your Asana token and workspace GID.

## Usage

```bash
asanable
```

## Development

```bash
ruff check src/ tests/ --fix
ruff format src/ tests/
pytest
```

## License

MIT
