# Evaluation Utilities

This directory contains evaluation scripts and a generic benchmark comparison runner.

## Benchmark Runner
Use `benchmark_runner.py` to generate a Markdown comparison report from a JSON config.

### Run
```bash
python eval/benchmark_runner.py \
  --config eval/benchmark_config.example.json \
  --compare-with eval/benchmark_config.previous.example.json \
  --threshold-config eval/thresholds.example.json \
  --output /tmp/benchmark_report.md \
  --output-json /tmp/benchmark_summary.json
```

If `--output` is omitted, the report is printed to stdout.

### Key options
- `--baseline-run`: override baseline run name from config
- `--compare-with`: previous config file to generate version-compare section
- `--threshold-config`: regression threshold rules for CI gate checks
- `--output-json`: write machine-readable summary for CI and release tooling
- `--enforce-thresholds`: exit non-zero if threshold checks fail

### Config Shape
```json
{
  "name": "finance-legal-h1-sprint-3",
  "domain": "general",
  "dataset_version": "v1",
  "run_id": "current",
  "baseline": "top_k",
  "lower_is_better": ["latency_ms", "cost_usd"],
  "runs": [
    {"name": "top_k", "metrics": {"accuracy": 0.32, "latency_ms": 920, "cost_usd": 0.011}},
    {"name": "cch_rse", "metrics": {"accuracy": 0.79, "latency_ms": 1080, "cost_usd": 0.018}}
  ]
}
```

### Output
The report includes:
- baseline selection
- metric table
- deltas vs baseline per run
- optional version-compare section
- simple winner summary by aggregate normalized score
- optional JSON gate summary (`passed`, `violations`)

## Domain presets
- Finance template: `eval/benchmarks/finance/benchmark_config.finance.example.json`
- Legal template: `eval/benchmarks/legal/benchmark_config.legal.example.json`
