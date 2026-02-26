# SDK Compatibility Policy (v1)

## Scope

This policy applies to:
- `dsrag.sdk` response envelope (`schema_version`, `ok`, `data/error`)
- SDK request dataclasses
- stable config schema (`dsrag.config.schema`)
- telemetry event schema (`dsrag.telemetry`)

## Compatibility guarantees

- Minor and patch releases MUST remain backward compatible for v1 contracts.
- Existing required fields MUST NOT be removed or renamed in v1.
- New fields MUST be additive and optional by default.
- Error code identifiers are stable within v1:
  - `INVALID_ARGUMENT`
  - `NOT_FOUND`
  - `INTERNAL_ERROR`

## Versioning rules

- Contract-breaking changes require a new major contract version.
- Breaking changes must include:
  - migration notes
  - release notes compatibility callout
  - explicit contract version bump

## Sensitive-value boundary

- Sensitive values must not appear in default exported schemas or telemetry payloads.
- Any opt-in sensitive export must be explicit (`include_sensitive=True`).

## Release process requirements

Each release must document:
- SDK contract compatibility status
- config schema compatibility status
- telemetry schema compatibility status
- migration actions (if any)
