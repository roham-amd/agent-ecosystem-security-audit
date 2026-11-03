# AESA engineering plan (post-assessment)

Derived from `aesa-independent-assessment-2026-11-03/` (baseline commit `82e3ec8328a4a4e54b7604fd7f09dafd041fbb74`).

## Milestone A — Correctness foundation (2.0.0)

| Rec | Status |
| --- | --- |
| R-001 corpus harness | Pilot expanded in 2.1.0 (8 cases) |
| R-002 canonical + CI | Done; monolith parity in 2.1.0 |
| R-003 semantic validation | Done (report + graph semantics pilot) |

## Milestone B — Architecture (2.0.0–2.1.0)

| Rec | Status |
| --- | --- |
| R-004 graph model | Schema + path search + semantic checks (no full engine) |
| R-005 inventory | Skill, MCP, A2A card, rules adapters |
| R-006 A2A/multimodal modules | Done |
| R-007 AISVS starter pack | Pilot |

## Milestone C — Next

| Rec | Status |
| --- | --- |
| R-001 full corpus families | In progress |
| R-008 SBOM/signature | Digest-only pilot (`aesa verify digest`) |
| R-009 runtime harness | Not started |
| R-011 SARIF | Not started |
| R-012 recipes | Starter (`docs/recipes/`) |

## Breaking change policy

- Report contract `audit_version: "1.0"` unchanged.
- Semantic validation may reject dangling references.
- Regenerated `audit.full.md` may differ from pre-2.1.0 monolith in §22–23 (sourced from `03-report-contract.md`).
