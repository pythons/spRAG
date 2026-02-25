import sys
import types
import unittest
from unittest.mock import patch

from dsrag.templates import (
    list_vertical_templates,
    get_vertical_template,
    apply_template_to_add_document_kwargs,
    apply_template_to_query_kwargs,
    query_with_template,
    create_kb_from_template,
)


class DummyKB:
    def __init__(self):
        self.last_kwargs = None

    def query(self, **kwargs):
        self.last_kwargs = kwargs
        return [{"ok": True}]


class TestTemplates(unittest.TestCase):
    def test_list_templates(self):
        templates = list_vertical_templates()
        self.assertIn("finance", templates)
        self.assertIn("legal", templates)

    def test_get_unknown_template_raises(self):
        with self.assertRaisesRegex(ValueError, "Unknown template"):
            get_vertical_template("unknown")

    def test_add_document_kwargs_merge(self):
        merged = apply_template_to_add_document_kwargs(
            "finance",
            {"chunking_config": {"chunk_size": 1024}},
        )
        self.assertEqual(merged["chunking_config"]["chunk_size"], 1024)
        self.assertTrue(merged["auto_context_config"]["get_section_summaries"])

    def test_query_kwargs_merge(self):
        merged = apply_template_to_query_kwargs(
            "legal",
            {"rse_params": "precise"},
        )
        self.assertEqual(merged["rse_params"], "precise")
        self.assertEqual(merged["vector_search_top_k"], 230)

    def test_query_with_template(self):
        kb = DummyKB()
        result = query_with_template(kb, "finance", ["q1"])
        self.assertEqual(result, [{"ok": True}])
        self.assertEqual(kb.last_kwargs["search_queries"], ["q1"])
        self.assertEqual(kb.last_kwargs["vector_search_top_k"], 240)

    def test_create_kb_from_template_uses_profile_default(self):
        fake_kb_module = types.ModuleType("dsrag.knowledge_base")

        class FakeKnowledgeBase:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        fake_kb_module.KnowledgeBase = FakeKnowledgeBase

        with patch.dict(sys.modules, {"dsrag.knowledge_base": fake_kb_module}):
            kb = create_kb_from_template("finance", kb_id="kb_fin")
            self.assertEqual(kb.kwargs["kb_id"], "kb_fin")
            self.assertEqual(kb.kwargs["profile"], "finance_default")


if __name__ == "__main__":
    unittest.main()
