# AESA security regression corpus (v0.1)

Pilot ground-truth cases for deterministic tooling (R-001). LLM procedure effectiveness is **not** fully benchmarked by this harness yet.

## Layout

- `fixtures/` — synthetic miniature repositories (benign, vulnerable, ambiguous cases expand over time).
- `cases/` — case manifests referencing fixtures and expected validator outcomes.
- `../validation/` — shared positive/negative JSON fixtures for schema and semantic validation.

## Run

```bash
cd tools && pip install -e ".[dev]"
aesa corpus run
```

## Ground-truth rules

1. Expected results must be derivable from fixture bytes visible to the auditor.
2. Each case lists negative expectations (what must not be claimed) as the corpus matures.
3. Adversarial cases use inert payloads only — no live exploits or secrets.

## Current coverage

| Case | Validates |
| --- | --- |
| CORPUS-001 | Passive inventory adapters (Skill + MCP config) |
| CORPUS-002 | Report JSON Schema + semantic validation (positive) |
| CORPUS-003 | Semantic validator rejects orphan evidence |
| CORPUS-004 | Ecosystem graph JSON Schema |

Planned: prompt-injection fixtures, A2A Agent Card tampering, supply-chain digest mismatch (R-001 expansion).
