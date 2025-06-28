# asanable

Asana daily digest CLI aggregator.

Aggregate your assigned Asana tasks into a single, prioritized daily digest.

## Features

- Fetch incomplete Asana tasks assigned to you, sorted by due date
- Score and prioritize: overdue > today > this week > later
- Rich CLI output with colored sections and summary
- Optional: daily scheduler, Slack and Telegram notifications

## Setup

```bash
git clone https://github.com/your-org/asanable.git && cd asanable
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Edit `.env` with your Asana personal access token and workspace GID.

## Usage

```bash
# Run the full digest
asanable

# Summary only (quiet mode)
asanable --quiet

# Filter by project (case-insensitive substring match)
asanable --project "Mobile App"
asanable -p admin

# Combine flags
asanable -p mobile -q

# Run as a daily scheduler
asanable --schedule
```

## Development

All common commands are available via `make`:

```bash
make install    # Install project with dev dependencies
make lint       # Run linter (with auto-fix)
make format     # Format code
make check      # Lint + format check (CI mode, no fix)
make test       # Run all tests
make cov        # Run tests with coverage report (80% threshold)
make run        # Run the digest
make quiet      # Run digest in quiet mode
make schedule   # Start the daily scheduler
make clean      # Remove build artifacts and caches
```

Or run commands directly:

```bash
# Run a specific test file
pytest tests/unit/test_priority_service.py -v

# Run a single test
pytest tests/unit/test_priority_service.py::TestScoring::test_overdue_gets_highest_score -v
```

## Architecture

```
CLI (main.py) → Services (business logic) → Clients (external APIs)
                     ↑
                Domain (pure entities)
                     ↓
               Renderers (CLI, HTML, Slack, Telegram)
```

| Layer | Responsibility |
|---|---|
| `domain/` | Pure dataclasses: `AsanaTask`, `DigestItem`, `Digest` |
| `clients/` | API wrappers returning domain entities (Asana SDK) |
| `services/` | Business logic: scoring, digest building |
| `renderers/` | Output formatting: rich CLI, HTML, Slack blocks, Telegram markdown |
| `scheduler/` | Daily cron via `schedule` lib |

## Configuration

All settings via environment variables (`.env` file). See `.env.example` for the full list.

| Variable | Required | Default | Description |
|---|---|---|---|
| `ASANA_ACCESS_TOKEN` | yes | — | Asana personal access token |
| `ASANA_WORKSPACE_GID` | yes | — | Asana workspace GID |
| `DIGEST_SCHEDULE_TIME` | no | `08:00` | Daily digest time (for `--schedule` mode) |
| `SLACK_WEBHOOK_URL` | no | — | Slack incoming webhook URL |
| `TELEGRAM_BOT_TOKEN` | no | — | Telegram bot token |
| `TELEGRAM_CHAT_ID` | no | — | Telegram chat ID |

## License

MIT
