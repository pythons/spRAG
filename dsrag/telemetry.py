import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Protocol


SENSITIVE_TELEMETRY_KEYS = {
    "password",
    "secret",
    "secret_key",
    "access_key",
    "access_secret",
    "api_key",
    "token",
    "auth_token",
}


def _is_sensitive_key(key: str) -> bool:
    normalized = key.lower()
    return (
        normalized in SENSITIVE_TELEMETRY_KEYS
        or normalized.endswith("_password")
        or normalized.endswith("_secret")
        or normalized.endswith("_token")
        or normalized.endswith("_api_key")
    )


def sanitize_telemetry_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        sanitized: Dict[str, Any] = {}
        for key, value in payload.items():
            if _is_sensitive_key(key):
                continue
            sanitized[key] = sanitize_telemetry_payload(value)
        return sanitized
    if isinstance(payload, list):
        return [sanitize_telemetry_payload(item) for item in payload]
    return payload


class TelemetrySink(Protocol):
    def emit(self, event: Dict[str, Any]) -> None:
        ...


class NullTelemetrySink:
    def emit(self, event: Dict[str, Any]) -> None:
        return None


class InMemoryTelemetrySink:
    def __init__(self):
        self._events: List[Dict[str, Any]] = []

    def emit(self, event: Dict[str, Any]) -> None:
        self._events.append(event)

    def get_events(self) -> List[Dict[str, Any]]:
        return list(self._events)


class LoggingTelemetrySink:
    def __init__(self, logger_name: str = "dsrag.telemetry"):
        self.logger = logging.getLogger(logger_name)

    def emit(self, event: Dict[str, Any]) -> None:
        self.logger.info("Telemetry event", extra={"telemetry_event": event})


def build_telemetry_event(
    event_type: str,
    kb_id: str,
    profile: str,
    status: str,
    payload: Optional[Dict[str, Any]] = None,
    duration_ms: Optional[float] = None,
    error: Optional[str] = None,
    event_version: str = "1.0",
) -> Dict[str, Any]:
    event: Dict[str, Any] = {
        "event_id": str(uuid.uuid4()),
        "event_version": event_version,
        "event_type": event_type,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "kb_id": kb_id,
        "profile": profile,
        "status": status,
        "payload": sanitize_telemetry_payload(payload or {}),
    }
    if duration_ms is not None:
        event["duration_ms"] = round(duration_ms, 2)
    if error:
        event["error"] = error
    return event


def emit_telemetry_event(
    sink: TelemetrySink,
    event_type: str,
    kb_id: str,
    profile: str,
    status: str,
    payload: Optional[Dict[str, Any]] = None,
    duration_ms: Optional[float] = None,
    error: Optional[str] = None,
    event_version: str = "1.0",
) -> Dict[str, Any]:
    event = build_telemetry_event(
        event_type=event_type,
        kb_id=kb_id,
        profile=profile,
        status=status,
        payload=payload,
        duration_ms=duration_ms,
        error=error,
        event_version=event_version,
    )
    sink.emit(event)
    return event


def now_ms() -> float:
    return time.perf_counter() * 1000
