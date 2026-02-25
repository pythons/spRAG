import ast
import json
from typing import Any, Optional


def serialize_metadata(metadata: Optional[dict]) -> str:
    """Serialize metadata to JSON for safe storage."""
    return json.dumps(metadata or {})


def deserialize_metadata(metadata: Any) -> dict:
    """Deserialize metadata from JSON with safe legacy fallback."""
    if metadata in (None, ""):
        return {}

    if isinstance(metadata, dict):
        return metadata

    if not isinstance(metadata, str):
        return {}

    try:
        loaded = json.loads(metadata)
        return loaded if isinstance(loaded, dict) else {}
    except json.JSONDecodeError:
        # Backward compatibility for legacy `str(dict)` payloads.
        try:
            loaded = ast.literal_eval(metadata)
            return loaded if isinstance(loaded, dict) else {}
        except (ValueError, SyntaxError):
            return {}
