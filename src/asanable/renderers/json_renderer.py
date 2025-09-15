"""JSON renderer — produces a JSON string from a Digest."""

import json
from dataclasses import asdict

from asanable.domain.digest import Digest


def render_json(digest: Digest) -> str:
    """Render a complete Digest to a JSON string."""
    data = asdict(digest)
    return json.dumps(data, default=str, indent=2)
