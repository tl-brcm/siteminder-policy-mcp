"""Shared utility helpers for formatting and parsing objects."""

import json

def default_formatter(obj: dict) -> str:
    """Return a simple multi-line string describing an object."""

    lines: list[str] = []
    if "name" in obj:
        lines.append(f"NAME: {obj['name']}")
    if "id" in obj:
        lines.append(f"ID: {obj['id']}")
    if "path" in obj:
        lines.append(f"PATH: {obj['path']}")
    if "desc" in obj and obj["desc"]:
        lines.append(f"DESC: {obj['desc']}")
    return "\n".join(lines)


def ensure_dict(obj: str | dict) -> dict:
    """Ensure ``obj`` is a ``dict``, parsing JSON strings when necessary."""

    if isinstance(obj, str):
        try:
            return json.loads(obj)
        except Exception as exc:
            raise ValueError("Input must be a dict or a valid JSON string") from exc
    return obj

def extract_core_fields(obj: dict) -> dict:
    """Extract a subset of useful fields from a SiteMinder detail response."""

    data = obj.get("data", {})
    core = {
        "id": data.get("id"),
        "type": data.get("type"),
        "Name": data.get("Name"),
        "parent": obj.get("parent"),
        "links": obj.get("links", {}),
    }
    return core
