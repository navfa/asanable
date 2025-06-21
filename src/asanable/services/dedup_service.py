"""Deduplication service — merges Asana tasks and Gmail notifications."""

from asanable.constants import ItemSource
from asanable.domain.digest import DigestItem
from asanable.domain.email import GmailMessage
from asanable.domain.task import AsanaTask


def build_digest_items(
    tasks: list[AsanaTask],
    emails: list[GmailMessage],
) -> list[DigestItem]:
    """Convert and deduplicate tasks + emails into unified digest items."""
    task_items = _convert_tasks(tasks)
    email_items = _convert_emails(emails)
    return _deduplicate(task_items, email_items)


def _convert_tasks(tasks: list[AsanaTask]) -> list[DigestItem]:
    """Map Asana tasks to digest items."""
    return [_task_to_item(task) for task in tasks]


def _convert_emails(emails: list[GmailMessage]) -> list[DigestItem]:
    """Map Gmail messages to digest items."""
    return [_email_to_item(email) for email in emails]


def _task_to_item(task: AsanaTask) -> DigestItem:
    """Convert a single Asana task to a digest item."""
    return DigestItem(
        title=task.name,
        source=ItemSource.ASANA,
        permalink=task.permalink_url,
        due_on=task.due_on,
        project_name=task.project_name,
        asana_task_gid=task.gid,
        is_overdue=task.is_overdue,
    )


def _email_to_item(email: GmailMessage) -> DigestItem:
    """Convert a single Gmail message to a digest item."""
    return DigestItem(
        title=email.subject,
        source=ItemSource.GMAIL,
        permalink="",
        snippet=email.snippet,
        gmail_message_id=email.message_id,
        asana_task_gid=email.asana_task_gid,
        is_unread=email.is_unread,
    )


def _deduplicate(
    task_items: list[DigestItem],
    email_items: list[DigestItem],
) -> list[DigestItem]:
    """Merge email items into matching task items, keep unmatched separately."""
    merged_gids: set[str] = set()
    result = []

    for task_item in task_items:
        matching_email = _find_matching_email(task_item, email_items)
        if matching_email is not None:
            result.append(_merge_items(task_item, matching_email))
            merged_gids.add(task_item.asana_task_gid)  # type: ignore[arg-type]
        else:
            result.append(task_item)

    for email_item in email_items:
        if email_item.asana_task_gid not in merged_gids:
            result.append(email_item)

    return result


def _build_gid_index(items: list[DigestItem]) -> dict[str, DigestItem]:
    """Index items by their Asana task GID for fast lookup."""
    return {item.asana_task_gid: item for item in items if item.asana_task_gid is not None}


def _find_matching_email(
    task_item: DigestItem,
    email_items: list[DigestItem],
) -> DigestItem | None:
    """Find an email item that references the same Asana task."""
    if task_item.asana_task_gid is None:
        return None
    for email_item in email_items:
        if email_item.asana_task_gid == task_item.asana_task_gid:
            return email_item
    return None


def _merge_items(task_item: DigestItem, email_item: DigestItem) -> DigestItem:
    """Enrich a task item with email context."""
    return DigestItem(
        title=task_item.title,
        source=task_item.source,
        permalink=task_item.permalink,
        due_on=task_item.due_on,
        project_name=task_item.project_name,
        snippet=email_item.snippet,
        asana_task_gid=task_item.asana_task_gid,
        gmail_message_id=email_item.gmail_message_id,
        is_overdue=task_item.is_overdue,
        is_unread=email_item.is_unread,
    )
