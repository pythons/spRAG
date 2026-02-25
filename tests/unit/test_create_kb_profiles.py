import tempfile
import unittest
import importlib
import sys
import types
from unittest.mock import patch


class TestCreateKBProfiles(unittest.TestCase):
    def _import_create_kb_with_stubs(self):
        stub_pypdf = types.ModuleType("pypdf")
        stub_pypdf.PdfReader = object
        stub_docx2txt = types.ModuleType("docx2txt")
        stub_docx2txt.process = lambda _file_path: ""
        stub_knowledge_base = types.ModuleType("dsrag.knowledge_base")
        stub_knowledge_base.KnowledgeBase = object

        with patch.dict(
            sys.modules,
            {
                "pypdf": stub_pypdf,
                "docx2txt": stub_docx2txt,
                "dsrag.knowledge_base": stub_knowledge_base,
            },
        ):
            if "dsrag.create_kb" in sys.modules:
                del sys.modules["dsrag.create_kb"]
            module = importlib.import_module("dsrag.create_kb")
        return module

    def test_create_kb_from_file_passes_profile_and_adds_document(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = f"{tmpdir}/sample.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("hello profile")

            create_kb_module = self._import_create_kb_with_stubs()
            with patch("dsrag.create_kb.KnowledgeBase") as kb_cls:
                kb_instance = kb_cls.return_value
                create_kb_module.create_kb_from_file(
                    kb_id="kb_file_profile_test",
                    file_path=file_path,
                    profile="finance_default",
                )

                kb_cls.assert_called_once_with(
                    "kb_file_profile_test",
                    title="kb_file_profile_test",
                    description="",
                    language="en",
                    exists_ok=False,
                    profile="finance_default",
                )
                kb_instance.add_document.assert_called_once_with(doc_id="sample.txt", text="hello profile")

    def test_create_kb_from_directory_passes_profile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_dir = f"{tmpdir}/docs"
            doc_path = f"{nested_dir}/a.txt"

            import os
            os.makedirs(nested_dir, exist_ok=True)
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write("directory content")

            create_kb_module = self._import_create_kb_with_stubs()
            with patch("dsrag.create_kb.KnowledgeBase") as kb_cls, patch("dsrag.create_kb.time.sleep"):
                kb_instance = kb_cls.return_value
                create_kb_module.create_kb_from_directory(
                    kb_id="kb_dir_profile_test",
                    directory=nested_dir,
                    profile="legal_default",
                )

                kb_cls.assert_called_once_with(
                    "kb_dir_profile_test",
                    title="kb_dir_profile_test",
                    description="",
                    language="en",
                    exists_ok=False,
                    profile="legal_default",
                )
                kb_instance.add_document.assert_called_once()
                call_kwargs = kb_instance.add_document.call_args.kwargs
                self.assertEqual(call_kwargs["doc_id"], "/a.txt")
                self.assertEqual(call_kwargs["text"], "directory content")


if __name__ == "__main__":
    unittest.main()
