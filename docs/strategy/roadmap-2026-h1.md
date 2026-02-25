# 2026 H1 Product Roadmap

## Summary
This roadmap focuses on technical leadership proof for dense-document RAG while improving developer adoption for AI application teams.

Primary strategy for H1 2026:
- Technical leadership proof as the North Star
- SDK-first delivery model
- Vertical-first focus on finance and legal use cases
- Bi-weekly release cadence

## Goals
- Sustain measurable retrieval quality leadership on hard, open-book QA tasks
- Reduce integration friction from install to first successful query
- Improve stability and compatibility across vector DB and model provider combinations
- Build evaluation and reporting workflows that are easy for external users to reproduce

## Success Metrics
- Quality:
  - Maintain or improve benchmark deltas for `CCH + RSE` over `Top-k baseline`
  - Publish comparable benchmark reports on each release cycle
- Adoption:
  - Improve time-to-first-value (install to first `kb.query()` success)
  - Decrease integration failure reports for provider and vector DB setup
- Reliability:
  - Close P0/P1 regressions within one release cycle
  - Keep high-signal compatibility matrix up to date

## Release Timeline (Bi-weekly)
### Phase A: Stability Foundation (Sprints 1-2)
- Compatibility fixes for DB and provider integrations
- Serialization/schema migration hardening
- Known issues matrix and troubleshooting baseline docs

### Phase B: Proof of Leadership (Sprints 3-5)
- Standardized benchmark runner and report format
- Version-to-version benchmark comparison in release notes
- Finance/legal evaluation presets and reproducible configurations

### Phase C: Vertical Experience (Sprints 6-8)
- Finance and legal profile defaults
- End-to-end vertical templates
- Diagnostics for common setup and runtime failures

### Phase D: Hosted-Readiness by Interface (Sprints 9-12)
- Structured telemetry event model
- Stable config schema with sensitive-value boundaries
- SDK-level interfaces that can back future managed offerings

## Scope Decisions
In scope:
- SDK capability, reliability, and docs
- Benchmarks, reproducibility, and release discipline
- Vertical quality optimization for finance/legal

Out of scope for this cycle:
- Full managed multi-tenant product
- Enterprise admin console and billing platform
- Broad vertical expansion outside finance/legal

## Risk Register
- Risk: Benchmarks improve while integration complexity grows
  - Mitigation: Track both quality and developer setup KPIs in each release
- Risk: Provider ecosystem changes break integrations
  - Mitigation: Compatibility matrix with explicit tested versions and fast patch policy
- Risk: Bi-weekly cadence degrades release quality
  - Mitigation: Enforce release gates with benchmark and regression checks

## Decision Log
- North Star: technical leadership proof
- Target users: AI application engineering teams
- Delivery: SDK-first, hosted-later
- Domain strategy: finance/legal vertical-first
- Release rhythm: bi-weekly
