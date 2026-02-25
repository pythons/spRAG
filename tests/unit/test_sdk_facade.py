import unittest
from unittest.mock import patch

from dsrag.sdk import (
    SDK_SCHEMA_VERSION,
    AddDocumentRequest,
    CreateKBRequest,
    DSRAGSDK,
    ExportConfigRequest,
    GetTelemetryRequest,
    QueryRequest,
)


class FakeSink:
    def __init__(self):
        self.events = [{"event_type": "query"}]

    def get_events(self):
        return list(self.events)


class FakeKB:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.telemetry_sink = kwargs.get("telemetry_sink", FakeSink())

    def add_document(self, **kwargs):
        if kwargs.get("doc_id") == "bad_doc":
            raise ValueError("bad document")
        return None

    def query(self, **kwargs):
        if kwargs.get("search_queries") == ["boom"]:
            raise RuntimeError("query failed")
        return [{"doc_id": "d1", "score": 1.0}]

    def export_config_schema(self, include_sensitive=False):
        return {
            "schema_version": "1.0",
            "kb_id": self.kwargs.get("kb_id", "unknown"),
            "kb": {"profile": self.kwargs.get("profile", "general_balanced")},
            "components": {},
            "include_sensitive": include_sensitive,
        }


class FakeKBNoTelemetry(FakeKB):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.telemetry_sink = object()


class TestSDKFacade(unittest.TestCase):
    def test_create_and_query_success(self):
        sdk = DSRAGSDK()
        with patch("dsrag.sdk._get_kb_class", return_value=FakeKB):
            create_resp = sdk.create_kb(
                CreateKBRequest(kb_id="kb1", profile="finance_default")
            )
            self.assertTrue(create_resp["ok"])
            self.assertEqual(create_resp["schema_version"], SDK_SCHEMA_VERSION)
            self.assertEqual(create_resp["data"]["kb_id"], "kb1")

            query_resp = sdk.query(
                QueryRequest(kb_id="kb1", search_queries=["what happened?"])
            )
            self.assertTrue(query_resp["ok"])
            self.assertEqual(query_resp["data"]["result_count"], 1)

    def test_error_mapping_invalid_argument(self):
        sdk = DSRAGSDK()
        with patch("dsrag.sdk._get_kb_class", return_value=FakeKB):
            sdk.create_kb(CreateKBRequest(kb_id="kb1"))
            resp = sdk.add_document(
                AddDocumentRequest(kb_id="kb1", doc_id="bad_doc", text="x")
            )
            self.assertFalse(resp["ok"])
            self.assertEqual(resp["error"]["code"], "INVALID_ARGUMENT")

    def test_export_config_success(self):
        sdk = DSRAGSDK()
        with patch("dsrag.sdk._get_kb_class", return_value=FakeKB):
            sdk.create_kb(CreateKBRequest(kb_id="kb2"))
            resp = sdk.export_config(ExportConfigRequest(kb_id="kb2"))
            self.assertTrue(resp["ok"])
            self.assertEqual(resp["data"]["config"]["schema_version"], "1.0")

    def test_get_telemetry_error_without_retrievable_sink(self):
        sdk = DSRAGSDK()
        with patch("dsrag.sdk._get_kb_class", return_value=FakeKBNoTelemetry):
            sdk.create_kb(CreateKBRequest(kb_id="kb3"))
            resp = sdk.get_telemetry(GetTelemetryRequest(kb_id="kb3"))
            self.assertFalse(resp["ok"])
            self.assertEqual(resp["error"]["code"], "INVALID_ARGUMENT")

    def test_run_diagnostics_success(self):
        sdk = DSRAGSDK()
        resp = sdk.run_diagnostics()
        self.assertTrue(resp["ok"])
        self.assertIn("report", resp["data"])


if __name__ == "__main__":
    unittest.main()
