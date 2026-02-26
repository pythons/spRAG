import tempfile
import unittest
import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "docs" / "operations" / "check_release_notes_gate.py"
SPEC = importlib.util.spec_from_file_location("check_release_notes_gate", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
check_release_notes_template = MODULE.check_release_notes_template


class TestReleaseNotesGate(unittest.TestCase):
    def test_gate_passes_when_required_headings_exist(self):
        content = """
# Release Notes Template
## SDK Contract Compatibility
## Schema and Telemetry Compatibility
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            path = f.name
        missing = check_release_notes_template(path)
        self.assertEqual(missing, [])

    def test_gate_fails_when_headings_missing(self):
        content = """
# Release Notes Template
## Compatibility
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            path = f.name
        missing = check_release_notes_template(path)
        self.assertIn("## SDK Contract Compatibility", missing)
        self.assertIn("## Schema and Telemetry Compatibility", missing)


if __name__ == "__main__":
    unittest.main()
