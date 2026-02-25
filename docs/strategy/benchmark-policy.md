# Benchmark Policy

## Purpose
Define a consistent, version-to-version benchmark policy for release decisions.

## Core Metrics
- Accuracy (higher is better)
- Latency (lower is better)
- Cost (lower is better)

## Comparison Rules
- Every release candidate must be compared against a previous benchmark config.
- Reports must include:
  - raw metrics
  - delta vs baseline
  - version compare (current vs previous baseline)
- Domain should be explicitly tagged (`general`, `finance`, `legal`).

## Regression Thresholds
- Threshold rules are defined in `eval/thresholds.example.json` (or project override).
- Sprint 1 mode:
  - warning-only (report violation but do not fail release gate)
- Sprint 2+ mode:
  - hard gate (threshold violations fail CI)

## Reproducibility Requirements
- Config must include:
  - `domain`
  - `dataset_version`
  - `run_id`
- Reports and JSON summaries are uploaded as CI artifacts for auditability.

## Release Note Requirements
Every release note should include:
- baseline name
- quality/latency/cost deltas
- short interpretation of tradeoffs
