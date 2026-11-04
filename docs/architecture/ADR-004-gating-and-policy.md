# ADR-004: Centralized gate semantics and repository policy

## Status

Accepted (AESA Guard 3.4)

## Context

Fail-on checks, PR annotations, risk deltas, and terminal reports each decided
independently which findings were “actionable,” which risked CAPABILITY noise
blocking CI and inconsistent `fail_on=any` behavior with baselines.

## Decision

1. **`aesa.security.gating`** is the single source of truth for gate classes
   (`SECURITY_FINDING`, `EXPOSURE`) and exit-code computation.
2. **`.aesa.yml`** supplies declarative defaults; explicit CLI flags win.
3. Suppressions require justification; optional `expires` fails closed when past.
4. Policy YAML uses a deterministic subset parser (no optional PyYAML) so CI and
   local installs behave identically.
5. `ScanResult.from_findings_doc` rebuilds explain/diff helpers without
   duplicating field mapping in the CLI.

## Consequences

- Adding a new gate class requires updating `gating.py` and tests once.
- CAPABILITY observations remain inventory-only under default policies.
- Extensibility for graph `Relationship` objects remains in `models.py` without
  forcing unused claim dataclasses into the runtime path.
