import json
import tempfile
import unittest
from pathlib import Path

from eval.benchmark_runner import load_config, render_markdown


class TestBenchmarkRunner(unittest.TestCase):
    def test_render_markdown_contains_sections(self):
        cfg = {
            "name": "test-report",
            "baseline": "top_k",
            "lower_is_better": ["latency_ms"],
            "runs": [
                {"name": "top_k", "metrics": {"accuracy": 0.3, "latency_ms": 1000}},
                {"name": "cch_rse", "metrics": {"accuracy": 0.8, "latency_ms": 1200}},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cfg.json"
            path.write_text(json.dumps(cfg), encoding="utf-8")
            loaded = load_config(path)
            md = render_markdown(loaded)

        self.assertIn("# Benchmark Report: test-report", md)
        self.assertIn("## Raw Metrics", md)
        self.assertIn("## Delta vs Baseline", md)
        self.assertIn("cch_rse", md)
