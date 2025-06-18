"""Slack renderer — sends a digest summary via webhook."""

import json
import urllib.request

import structlog

from asanable.domain.digest import Digest

logger = structlog.get_logger()

SLACK_TIMEOUT_SECONDS = 10


def send_slack_digest(digest: Digest, webhook_url: str) -> None:
    """Send a formatted digest summary to a Slack channel."""
    payload = _build_payload(digest)
    _post_webhook(webhook_url, payload)


def _build_payload(digest: Digest) -> dict:
    """Build a Slack blocks payload from a digest."""
    summary = digest.summary
    header_text = (
        f"*Daily Digest* — {summary.generated_at:%Y-%m-%d}\n"
        f"Total: *{summary.total_items}*  |  "
        f"Overdue: *{summary.overdue_count}*  |  "
        f"Today: *{summary.today_count}*"
    )

    blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": header_text}},
        {"type": "divider"},
    ]

    for section in digest.sections:
        section_lines = [f"*{section.section_type.value.replace('_', ' ').title()}*"]
        for item in section.items:
            due = item.due_on.strftime("%b %d") if item.due_on else ""
            line = f"• {item.title}"
            if due:
                line += f" _{due}_"
            section_lines.append(line)
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": "\n".join(section_lines)},
        })

    return {"blocks": blocks}


def _post_webhook(url: str, payload: dict) -> None:
    """Send a JSON payload to a Slack webhook URL."""
    data = json.dumps(payload).encode()
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(request, timeout=SLACK_TIMEOUT_SECONDS)
