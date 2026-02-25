# Evaluation Utilities

This directory contains evaluation scripts and a generic benchmark comparison runner.

## Benchmark Runner
Use `benchmark_runner.py` to generate a Markdown comparison report from a JSON config.

### Run
```bash
python eval/benchmark_runner.py --config eval/benchmark_config.example.json --output /tmp/benchmark_report.md
```

If `--output` is omitted, the report is printed to stdout.

### Config Shape
```json
{
  "name": "finance-legal-h1-sprint-3",
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
- simple winner summary by aggregate normalized score
