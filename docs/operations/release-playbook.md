# Release Playbook

## Purpose
Define a repeatable bi-weekly release process that balances model quality gains, reliability, and developer experience.

## Cadence
- Week 1:
  - Feature and fix implementation
  - Integration validation
  - Benchmark dry runs
- Week 2:
  - Regression and compatibility testing
  - Benchmark report finalization
  - Docs and release notes publication

## Release Gates
- Code quality:
  - CI green for unit and integration suites
  - No unresolved P0 issues
- Product quality:
  - Benchmark comparison report generated
  - Significant quality regressions explained or release blocked
- Developer quality:
  - Quickstart still valid
  - Known issues matrix refreshed

## Release Artifacts
- Changelog entries by category:
  - Added
  - Changed
  - Fixed
  - Compatibility
  - Security
- Benchmark report:
  - Baseline vs candidate summary
  - Accuracy/latency/cost deltas
  - Domain notes for finance/legal scenarios
- Updated docs:
  - Installation and integration notes
  - Known issues matrix
  - Migration notes if schema or config changed

## Escalation Policy
- P0:
  - Stop release
  - Patch immediately
- P1:
  - Can release only with documented workaround and target fix date
- P2/P3:
  - Track in backlog and roadmap updates

## Ownership
- Product:
  - Prioritize scope and release decision
- Engineering:
  - Execute implementation, tests, and compatibility checks
- Docs/DevRel:
  - Publish release notes and troubleshooting guidance
