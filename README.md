# asanable

Prioritized daily digest for your Asana tasks — overdue, today, this week — straight in your terminal.

![asanable screenshot](public/screenshots/screen.png)

## Installation

```bash
pip install asanable
```

## Features

- Fetch incomplete Asana tasks assigned to you, sorted by due date
- Score and prioritize: overdue > today > this week > later
- Rich CLI output with colored sections and project summary
- Mark tasks as done directly from the terminal
- Open tasks in the browser
- Local cache for instant offline access
- Filter by project or section (overdue, today)
- Export as HTML
- Optional: daily scheduler, Slack and Telegram notifications

## Quick Start

```bash
# Install
pip install asanable

# Interactive setup (creates .env with your token and workspace)
asanable --init

# Run your first digest
asanable
```

## Setup (manual)

```bash
git clone https://github.com/navfa/asanable.git && cd asanable
cp .env.example .env
pip install -e ".[dev]"
```

Edit `.env` with your Asana personal access token and workspace GID.

## Usage

```bash
# First time setup (interactive wizard)
asanable --init

# Run the full digest
asanable

# Summary only (quiet mode)
asanable --quiet

# Filter by project (case-insensitive substring match)
asanable --project "Mobile App"
asanable -p admin

# Use cached data (no API call, instant)
asanable --cache

# Force refresh from API
asanable --refresh

# Show only overdue tasks
asanable --overdue

# Show only tasks due today
asanable --today

# Export as HTML
asanable --output html > digest.html

# Mark a task as done
asanable --done 1234567890

# Open a task in the browser
asanable --open 1234567890

# Combine flags
asanable -p mobile -q
asanable --cache --overdue
asanable --cache -o html > mobile.html

# Run as a daily scheduler
asanable --schedule

# Show version
asanable --version
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
make project P="Mobile App"  # Filter by project
make html       # Export digest as HTML to stdout
make init       # Run interactive setup wizard
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
