import unittest

from dsrag.telemetry import (
    InMemoryTelemetrySink,
    build_telemetry_event,
    emit_telemetry_event,
    sanitize_telemetry_payload,
)


class TestTelemetry(unittest.TestCase):
    def test_sanitize_payload_removes_sensitive_fields(self):
        payload = {
            "doc_id": "a",
            "api_key": "secret",
            "nested": {
                "token": "abc",
                "safe": 1,
            },
            "list": [{"password": "x", "name": "ok"}],
        }
        sanitized = sanitize_telemetry_payload(payload)
        self.assertEqual(sanitized["doc_id"], "a")
        self.assertNotIn("api_key", sanitized)
        self.assertEqual(sanitized["nested"], {"safe": 1})
        self.assertEqual(sanitized["list"], [{"name": "ok"}])

    def test_build_event_has_core_fields(self):
        event = build_telemetry_event(
            event_type="query",
            kb_id="kb_1",
            profile="general_balanced",
            status="success",
            payload={"num_results": 3},
            duration_ms=12.3456,
        )
        self.assertEqual(event["event_type"], "query")
        self.assertEqual(event["kb_id"], "kb_1")
        self.assertEqual(event["profile"], "general_balanced")
        self.assertEqual(event["status"], "success")
        self.assertEqual(event["duration_ms"], 12.35)
        self.assertEqual(event["payload"]["num_results"], 3)
        self.assertIn("event_id", event)
        self.assertIn("timestamp_utc", event)

    def test_emit_event_to_memory_sink(self):
        sink = InMemoryTelemetrySink()
        emit_telemetry_event(
            sink=sink,
            event_type="add_document",
            kb_id="kb_2",
            profile="finance_default",
            status="error",
            error="boom",
            payload={"token": "hidden", "doc_id": "doc_1"},
        )
        events = sink.get_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["status"], "error")
        self.assertEqual(events[0]["error"], "boom")
        self.assertEqual(events[0]["payload"], {"doc_id": "doc_1"})


if __name__ == "__main__":
    unittest.main()
