# AESA agent detection benchmark (v0.1.0)

Measures **whether assessments find expected agent-ecosystem issues**, separate from the tooling corpus under `tests/corpus/`.

## Current scope

`aesa benchmark run` checks **deterministic inventory expectations** against synthetic fixtures and records ground-truth finding stubs for future LLM scoring.

It does **not** invoke Cursor, Claude, or other models yet. Do not cite pass rates as detection quality for AI auditors until a model runner and reviewed ground truth are wired.

## Layout

- `fixtures/` — miniature repos (benign, injection, privilege path)
- `cases/BENCH-*.json` — expectations + optional `ground_truth_findings`

## Run

```bash
cd tools && pip install -e ".[dev]"
aesa benchmark run
```

## Ground-truth rules

1. Expected inventory facts must be derivable from fixture bytes.
2. Finding stubs must state attacker control → privileged effect and required evidence.
3. Adversarial fixtures stay inert — no live exploits or real secrets.
