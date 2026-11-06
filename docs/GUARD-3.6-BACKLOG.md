# authdiff / AESA Guard 3.6 implementation backlog

North-star remains **Authority Diff** on one facts engine.

Status key: `done` · `in_progress` · `next` · `deferred` · `frozen`

## Milestone W1 — Installable and honest

| ID | Deliverable | Status |
| --- | --- | --- |
| W1.1–W1.8 | Install crash, FP hotfixes, decision honesty, aliases | done |
| W1.9 | Publish PyPI (`aesa-tools`) via trusted publishing | next (workflow ready) |
| W1.10 | Docker → `python:3.12.16-slim-trixie` | done |

## Milestone W2–W3 — Facts + Authority Diff

| ID | Deliverable | Status |
| --- | --- | --- |
| W2.1–W2.2 | Claude settings + JSONC MCP | done |
| W3.1–W3.3 | Base-vs-head Action + advisory init | done |
| Product rename to **authdiff** | done (`aesa` compat alias) |
| Physical archive `archive/methodology/` | done |

## Milestone W4 / 90-day

| ID | Deliverable | Status |
| --- | --- | --- |
| W4.1 | Atlas crawl harness (target N≥300) | done (seed; expand via seed JSON) |
| W4.2 | Benign corpus must not BLOCK | done |
| W4.3 | Attack-replay corpus | done (`examples/attack-replay/`) |
| D61 | Artifact-level vet (`authdiff artifact-vet`) | done (registry metadata) |
| D62 | Sandboxed tools/list snapshot | done (`authdiff snapshot`) |
| D63 | Sigstore + SBOM workflow | done (`.github/workflows/sigstore-release.yml`) |

## Radical alternatives

| ID | Deliverable | Status |
| --- | --- | --- |
| R1 | Authority broker `authdiff run` | done (MVP env scrub) |
| R2 | Attack-replay Metasploitable set | done |
| R3 | AUTHORITY schemas + `lsp-validate` | done (full LSP deferred) |

See [`RADICAL-ALTERNATIVES.md`](RADICAL-ALTERNATIVES.md).
