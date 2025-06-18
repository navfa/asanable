"""Telegram renderer — sends a digest summary via Bot API."""

import json
import urllib.request

import structlog

from asanable.domain.digest import Digest

logger = structlog.get_logger()

TELEGRAM_API_BASE = "https://api.telegram.org/bot"
TELEGRAM_TIMEOUT_SECONDS = 10
TELEGRAM_PARSE_MODE = "Markdown"


def send_telegram_digest(digest: Digest, bot_token: str, chat_id: str) -> None:
    """Send a formatted digest summary to a Telegram chat."""
    text = _build_message(digest)
    _send_message(bot_token, chat_id, text)


def _build_message(digest: Digest) -> str:
    """Build a Markdown-formatted message from a digest."""
    summary = digest.summary
    lines = [
        f"*Daily Digest* — {summary.generated_at:%Y-%m-%d}",
        f"Total: *{summary.total_items}* | Overdue: *{summary.overdue_count}* | Today: *{summary.today_count}*",
        "",
    ]

    for section in digest.sections:
        section_title = section.section_type.value.replace("_", " ").title()
        lines.append(f"*{section_title}*")
        for item in section.items:
            due = f" _{item.due_on.strftime('%b %d')}_" if item.due_on else ""
            lines.append(f"• {item.title}{due}")
        lines.append("")

    return "\n".join(lines).strip()


def _send_message(bot_token: str, chat_id: str, text: str) -> None:
    """Send a message via the Telegram Bot API."""
    url = f"{TELEGRAM_API_BASE}{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": TELEGRAM_PARSE_MODE,
    }
    data = json.dumps(payload).encode()
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(request, timeout=TELEGRAM_TIMEOUT_SECONDS)
