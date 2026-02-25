import unittest

from dsrag.config.schema import (
    CONFIG_SCHEMA_VERSION,
    build_stable_kb_config_schema,
    redact_sensitive_config,
    validate_stable_kb_config_schema,
)


class TestConfigSchema(unittest.TestCase):
    def test_redact_sensitive_config(self):
        data = {
            "api_key": "secret",
            "nested": {
                "token": "abc",
                "safe": 123,
            },
            "providers": [
                {"name": "x", "password": "p"},
                {"name": "y", "ok": True},
            ],
        }
        redacted = redact_sensitive_config(data)
        self.assertNotIn("api_key", redacted)
        self.assertEqual(redacted["nested"], {"safe": 123})
        self.assertEqual(redacted["providers"], [{"name": "x"}, {"name": "y", "ok": True}])

    def test_build_stable_schema(self):
        config = build_stable_kb_config_schema(
            kb_id="kb_1",
            kb_metadata={
                "title": "T",
                "description": "D",
                "language": "en",
                "supp_id": "s1",
                "profile": "general_balanced",
                "created_on": 123,
            },
            components={
                "embedding_model": {"provider": "openai", "api_key": "x"},
                "vector_db": {"table_name": "t"},
            },
            include_sensitive=False,
        )
        self.assertEqual(config["schema_version"], CONFIG_SCHEMA_VERSION)
        self.assertEqual(config["kb_id"], "kb_1")
        self.assertEqual(config["kb"]["profile"], "general_balanced")
        self.assertNotIn("api_key", config["components"]["embedding_model"])

    def test_validate_stable_schema(self):
        config = {
            "schema_version": CONFIG_SCHEMA_VERSION,
            "kb_id": "kb_2",
            "kb": {"title": "x"},
            "components": {"embedding_model": {"model": "m"}},
        }
        validate_stable_kb_config_schema(config)

        with self.assertRaisesRegex(ValueError, "Unsupported config schema_version"):
            invalid = dict(config)
            invalid["schema_version"] = "999.0"
            validate_stable_kb_config_schema(invalid)


if __name__ == "__main__":
    unittest.main()
