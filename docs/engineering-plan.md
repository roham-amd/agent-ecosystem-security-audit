# AESA engineering plan

Tracks implementation against independent assessments and the [AESA 3.0 product specification](AESA-3.0-PRODUCT-SPEC.md).

## Milestone A — Correctness foundation (2.0.0)

| Rec | Status |
| --- | --- |
| R-001 corpus harness | Expanded (CORPUS-001–010) |
| R-002 canonical + CI | Done; monolith parity |
| R-003 semantic validation | Done (report + graph) |

## Milestone B — Architecture (2.0–2.1)

| Rec | Status |
| --- | --- |
| R-004 graph model | Schema + path search + semantic checks |
| R-005 inventory | Skills, MCP, A2A, rules, hooks, plugins, subagents, automations, CI workflows |
| R-006 A2A/multimodal modules | Done |
| R-007 AISVS starter pack | Pilot |

## Milestone C — Interop (2.2)

| Rec | Status |
| --- | --- |
| R-008 SBOM/signature | Digest-only pilot |
| R-009 runtime harness | Schema only — no harness |
| R-011 SARIF | Done (`aesa export sarif`) |
| R-012 recipes | `docs/recipes/` |

## Milestone D — Product experience (2.3–3.0)

| Item | Status |
| --- | --- |
| Bounded collector I/O | Done |
| Native AI skill | Done (`skills/`) |
| Unified `aesa audit` + profiles | Done (3.0.0) |
| Consumer GitHub Action | Done (composite + example) |
| Agent detection benchmark scaffold | Done (`aesa benchmark run`) |
| LLM finding precision/recall runner | Not started |
| PyPI published package | Not started |
| Hosted web workspace | Deferred |

## Breaking change policy

- Report contract `audit_version: "1.0"` unchanged in 3.0.0.
- Product major 3.0 reflects UX/packaging (unified audit, Assessment framing, Action).
- Semantic validation may reject dangling references.
