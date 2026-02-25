# Troubleshooting

This guide maps common setup/runtime failures to concrete checks.

## Step 1: Run diagnostics

```python
from dsrag import run_diagnostics
print(run_diagnostics())
```

## Common issues

| Symptom | Likely Cause | What to Check | Action |
|---|---|---|---|
| `ModuleNotFoundError` for provider/vector DB package | Optional dependency not installed | `report["dependencies"]` in diagnostics output | Install the corresponding optional extra (e.g. `pip install "dsrag[openai,chroma]"`) |
| Auth failure from model provider | Missing API key env var | `report["environment"]` in diagnostics output | Export required env var and restart shell/session |
| Query returns empty results | Too strict filters or weak retrieval parameters | `metadata_filter`, `rse_params`, `vector_search_top_k` | Remove/relax filter, increase `vector_search_top_k`, or switch to profile defaults |
| Slow query latency | Large corpus + high retrieval breadth | `vector_search_top_k`, benchmark reports | Reduce top-k for latency-sensitive flows; keep high-top-k for quality-critical flows |
| Inconsistent behavior after upgrades | Config/schema drift or environment mismatch | release notes + known issues matrix | Compare against `docs/operations/known-issues-matrix.md` and re-run benchmark gates |

## Operational references

- Known issues matrix: `docs/operations/known-issues-matrix.md`
- Release playbook: `docs/operations/release-playbook.md`
- Benchmark policy: `docs/strategy/benchmark-policy.md`
