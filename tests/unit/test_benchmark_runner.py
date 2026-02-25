import json
import tempfile
import unittest
from pathlib import Path

from eval.benchmark_runner import (
    delta_vs_baseline,
    evaluate_thresholds,
    load_config,
    load_thresholds,
    render_markdown,
)


class TestBenchmarkRunner(unittest.TestCase):
    def test_render_markdown_contains_sections(self):
        cfg = {
            "name": "test-report",
            "domain": "general",
            "dataset_version": "v1",
            "run_id": "current",
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

    def test_threshold_violation_detected(self):
        cfg = {
            "name": "threshold-test",
            "domain": "general",
            "dataset_version": "v1",
            "run_id": "current",
            "baseline": "top_k",
            "lower_is_better": ["latency_ms"],
            "runs": [
                {"name": "top_k", "metrics": {"accuracy": 0.7, "latency_ms": 1000}},
                {"name": "candidate", "metrics": {"accuracy": 0.6, "latency_ms": 1200}},
            ],
        }
        threshold_cfg = {
            "thresholds": [
                {"metric": "accuracy", "direction": "higher_is_better", "max_regression_pct": 5.0}
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "cfg.json"
            thr_path = Path(tmp) / "thr.json"
            cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
            thr_path.write_text(json.dumps(threshold_cfg), encoding="utf-8")
            loaded = load_config(cfg_path)
            rules = load_thresholds(thr_path)
            deltas = delta_vs_baseline(loaded)
            passed, violations = evaluate_thresholds(deltas, rules)

        self.assertFalse(passed)
        self.assertGreaterEqual(len(violations), 1)
