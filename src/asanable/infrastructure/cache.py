"""Local cache for digest data — enables offline mode."""

import json
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from pathlib import Path

import structlog

from asanable.domain.task import AsanaTask

logger = structlog.get_logger()

CACHE_DIR_NAME = "asanable"
CACHE_FILE_NAME = "last_tasks.json"
DEFAULT_TTL_HOURS = 24


def get_cache_path() -> Path:
    """Return the cache file path following XDG conventions."""
    xdg_cache = Path.home() / ".cache"
    return xdg_cache / CACHE_DIR_NAME / CACHE_FILE_NAME


def save_tasks(tasks: list[AsanaTask]) -> None:
    """Persist tasks to the local cache."""
    cache_path = get_cache_path()
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "cached_at": datetime.now(tz=UTC).isoformat(),
        "tasks": [_task_to_dict(task) for task in tasks],
    }
    cache_path.write_text(json.dumps(payload, default=str))
    logger.debug("cache_saved", path=str(cache_path), count=len(tasks))


def load_tasks(ttl_hours: int = DEFAULT_TTL_HOURS) -> list[AsanaTask] | None:
    """Load tasks from cache if present and not expired. Returns None if stale or missing."""
    cache_path = get_cache_path()
    if not cache_path.exists():
        return None

    try:
        payload = json.loads(cache_path.read_text())
    except (json.JSONDecodeError, OSError):
        logger.warning("cache_read_failed", path=str(cache_path))
        return None

    if _is_expired(payload, ttl_hours):
        logger.debug("cache_expired", path=str(cache_path))
        return None

    tasks = [_dict_to_task(d) for d in payload.get("tasks", [])]
    logger.debug("cache_loaded", count=len(tasks))
    return tasks


def _is_expired(payload: dict, ttl_hours: int) -> bool:
    """Check if the cache payload has exceeded its TTL."""
    cached_at_str = payload.get("cached_at")
    if cached_at_str is None:
        return True
    cached_at = datetime.fromisoformat(cached_at_str)
    return datetime.now(tz=UTC) - cached_at > timedelta(hours=ttl_hours)


def _task_to_dict(task: AsanaTask) -> dict:
    """Serialize an AsanaTask to a JSON-safe dict."""
    data = asdict(task)
    if data["due_on"] is not None:
        data["due_on"] = data["due_on"].isoformat()
    return data


def _dict_to_task(data: dict) -> AsanaTask:
    """Deserialize a dict back to an AsanaTask."""
    from datetime import date

    due_on = date.fromisoformat(data["due_on"]) if data.get("due_on") else None
    return AsanaTask(
        gid=data["gid"],
        name=data["name"],
        due_on=due_on,
        project_name=data.get("project_name"),
        section_name=data.get("section_name"),
        permalink_url=data.get("permalink_url", ""),
    )
