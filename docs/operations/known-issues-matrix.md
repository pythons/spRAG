# Known Issues Matrix

## Purpose
Track high-signal compatibility and reliability issues in one place for users and maintainers.

## Status Definitions
- Open: Issue exists with no validated workaround
- Mitigated: Workaround available
- Fixed: Fix merged and released

## Matrix
| Area | Component | Symptom | Workaround | Status |
|---|---|---|---|---|
| Vector DB | Weaviate | Connection/setup incompatibility on specific client versions | Pin tested client versions and verify gRPC settings | Mitigated |
| Chat DB | SQLite chat thread | Legacy rows can fail JSON parsing | Fallback parser for legacy payload formats | Fixed |
| Metadata | Persistent config | Legacy metadata payload parsing inconsistencies | Safe parser and schema/version migration path | Fixed |
| Providers | Gemini/OpenAI-compatible | Provider package/import mismatch can fail at runtime | Use lazy imports and explicit dependency guidance | Mitigated |
| Retrieval Perf | Large top_k defaults | Query-time latency spikes on large corpora | Tune vector_search_top_k per workload | Mitigated |

## Update Policy
- Refresh at every bi-weekly release
- Link each row to issue IDs and release notes in PR descriptions
- Remove rows only after one stable release cycle with no regressions
