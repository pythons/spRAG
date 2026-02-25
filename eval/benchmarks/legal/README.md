# Legal Benchmark Preset

Use this config template as a starting point for legal-domain benchmark runs.

Example:
```bash
python eval/benchmark_runner.py \
  --config eval/benchmarks/legal/benchmark_config.legal.example.json \
  --compare-with eval/benchmark_config.previous.example.json \
  --output benchmark_legal.md \
  --output-json benchmark_legal.json
```
