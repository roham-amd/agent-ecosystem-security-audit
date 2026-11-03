# AgentSecBench (v0.2.0)

Measures **whether assessments find expected agent-ecosystem issues**, separate from the tooling corpus under `tests/corpus/`.

## Current scope

`aesa benchmark run` checks:

1. Deterministic inventory expectations against synthetic fixtures.
2. Deterministic **AESA Guard rule** expectations (`expect_rule_ids` / `forbid_rule_ids`).
3. Records expert-oriented `ground_truth_findings` stubs for future LLM scoring.

It does **not** invoke Cursor, Claude, or other models yet. Do not cite pass rates as detection quality for AI auditors until a model runner and reviewed ground truth are wired.

## Layout

- `fixtures/` — miniature repos (benign, injection, privilege path)
- `cases/BENCH-*.json` — expectations + optional `ground_truth_findings`

## Run

```bash
cd tools && uv sync --locked
aesa benchmark run
```

## Ground-truth rules

1. Expected inventory facts must be derivable from fixture bytes.
2. Finding stubs must state attacker control → privileged effect and required evidence.
3. Adversarial fixtures stay inert — no live exploits or real secrets.
4. Keep tooling corpus (`tests/corpus`) separate from AgentSecBench detection cases.
