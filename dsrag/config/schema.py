from copy import deepcopy
from typing import Any, Dict


CONFIG_SCHEMA_VERSION = "1.0"
SUPPORTED_CONFIG_SCHEMA_VERSIONS = {CONFIG_SCHEMA_VERSION}

SENSITIVE_CONFIG_KEYS = {
    "password",
    "secret",
    "secret_key",
    "access_key",
    "access_secret",
    "api_key",
    "token",
    "auth_token",
    "weaviate_secret",
}


def _is_sensitive_key(key: str) -> bool:
    normalized_key = key.lower()
    return (
        normalized_key in SENSITIVE_CONFIG_KEYS
        or normalized_key.endswith("_password")
        or normalized_key.endswith("_secret")
        or normalized_key.endswith("_token")
        or normalized_key.endswith("_api_key")
    )


def redact_sensitive_config(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: Dict[str, Any] = {}
        for key, nested_value in value.items():
            if _is_sensitive_key(key):
                continue
            redacted[key] = redact_sensitive_config(nested_value)
        return redacted
    if isinstance(value, list):
        return [redact_sensitive_config(v) for v in value]
    return value


def build_stable_kb_config_schema(
    kb_id: str,
    kb_metadata: Dict[str, Any],
    components: Dict[str, Any],
    include_sensitive: bool = False,
) -> Dict[str, Any]:
    schema = {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "kb_id": kb_id,
        "kb": {
            "title": kb_metadata.get("title", ""),
            "description": kb_metadata.get("description", ""),
            "language": kb_metadata.get("language", "en"),
            "supp_id": kb_metadata.get("supp_id", ""),
            "profile": kb_metadata.get("profile", "general_balanced"),
            "created_on": kb_metadata.get("created_on"),
        },
        "components": deepcopy(components),
    }
    if include_sensitive:
        return schema
    return redact_sensitive_config(schema)


def validate_stable_kb_config_schema(config: Dict[str, Any]) -> None:
    if not isinstance(config, dict):
        raise ValueError("Config must be a dictionary.")
    schema_version = config.get("schema_version")
    if schema_version not in SUPPORTED_CONFIG_SCHEMA_VERSIONS:
        supported = ", ".join(sorted(SUPPORTED_CONFIG_SCHEMA_VERSIONS))
        raise ValueError(
            f"Unsupported config schema_version '{schema_version}'. Supported: {supported}"
        )
    if "kb_id" not in config or not config["kb_id"]:
        raise ValueError("Config must include non-empty 'kb_id'.")
    if "kb" not in config or not isinstance(config["kb"], dict):
        raise ValueError("Config must include 'kb' object.")
    if "components" not in config or not isinstance(config["components"], dict):
        raise ValueError("Config must include 'components' object.")
