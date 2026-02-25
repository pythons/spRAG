# Telemetry

dsRAG includes a structured telemetry event model for ingestion/query lifecycle events.

## Event schema

Each event includes:
- `event_id`
- `event_version`
- `event_type`
- `timestamp_utc`
- `kb_id`
- `profile`
- `status`
- `duration_ms` (when available)
- `payload` (sanitized)
- `error` (when status is `error`)

Sensitive keys (for example `api_key`, `token`, `password`) are removed from payloads.

## Built-in sinks

```python
from dsrag import InMemoryTelemetrySink, LoggingTelemetrySink
```

- `InMemoryTelemetrySink`: keeps events in memory for tests/debugging.
- `LoggingTelemetrySink`: emits events to Python logging (`dsrag.telemetry`).

## Usage

```python
from dsrag import InMemoryTelemetrySink
from dsrag.knowledge_base import KnowledgeBase

sink = InMemoryTelemetrySink()
kb = KnowledgeBase(kb_id="telemetry_demo", telemetry_sink=sink)

# run kb.add_document(...) / kb.query(...)
events = sink.get_events()
print(events[-1])
```
