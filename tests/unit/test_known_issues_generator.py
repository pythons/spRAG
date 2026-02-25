import tempfile
import unittest
from pathlib import Path

from docs.operations.generate_known_issues import load_source, render_markdown


class TestKnownIssuesGenerator(unittest.TestCase):
    def test_render_markdown_includes_matrix_rows(self):
        payload = """
{
  "status_definitions": [
    {"name": "Open", "description": "No workaround"}
  ],
  "items": [
    {
      "area": "Vector DB",
      "component": "Weaviate",
      "symptom": "setup issue",
      "workaround": "pin version",
      "status": "Open"
    }
  ]
}
""".strip()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "known-issues.yaml"
            source.write_text(payload, encoding="utf-8")
            data = load_source(source)
            md = render_markdown(data)

        self.assertIn("# Known Issues Matrix", md)
        self.assertIn("| Vector DB | Weaviate |", md)
        self.assertIn("- Open: No workaround", md)
