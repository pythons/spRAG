import unittest

from dsrag.database.chunk.metadata_utils import (
    deserialize_metadata,
    serialize_metadata,
)


class TestMetadataUtils(unittest.TestCase):
    def test_serialize_and_deserialize_json_metadata(self):
        metadata = {"source": "doc", "page": 3}
        serialized = serialize_metadata(metadata)
        deserialized = deserialize_metadata(serialized)
        self.assertEqual(deserialized, metadata)

    def test_deserialize_legacy_repr_metadata(self):
        legacy = "{'source': 'legacy', 'page': 7}"
        deserialized = deserialize_metadata(legacy)
        self.assertEqual(deserialized, {"source": "legacy", "page": 7})

    def test_deserialize_invalid_metadata_returns_empty_dict(self):
        self.assertEqual(deserialize_metadata("not-json"), {})
        self.assertEqual(deserialize_metadata(None), {})
