import json

def default_formatter(obj: dict) -> str:
    lines = []
    if "name" in obj:
        lines.append(f"NAME: {obj['name']}")
    if "id" in obj:
        lines.append(f"ID: {obj['id']}")
    if "path" in obj:
        lines.append(f"PATH: {obj['path']}")
    if "desc" in obj and obj["desc"]:
        lines.append(f"DESC: {obj['desc']}")
    return "\n".join(lines)


def ensure_dict(obj):
    """
    Accepts dict or JSON string, returns dict.
    Raises ValueError if parsing fails.
    """
    if isinstance(obj, str):
        try:
            return json.loads(obj)
        except Exception:
            raise ValueError("Input must be a dict or a valid JSON string")
    return obj

def extract_core_fields(obj):
    """
    Extracts core fields (id, type, Name, parent, links) from SiteMinder object detail response.
    Returns a dict with those fields if present.
    """
    data = obj.get("data", {})
    core = {
        "id": data.get("id"),
        "type": data.get("type"),
        "Name": data.get("Name"),
        "parent": obj.get("parent", None),
        "links": obj.get("links", {}),
    }
    return core
