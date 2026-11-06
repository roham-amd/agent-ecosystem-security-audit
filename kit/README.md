# Methodology kit (optional deep mode)

AESA Guard’s product path is **`doctor` → `vet` → `init-gate` → `scan`**.

The materials below are the **optional** deep-assessment kit (procedure 1.0).
They are not required to run the Authority Diff gate.

| Path | Role |
| --- | --- |
| [`../prompts/`](../prompts/) | Audit procedure, passive guardrails, scan-triage |
| [`../modules/`](../modules/) | On-demand component checklists (load only what you need) |
| [`../control-packs/`](../control-packs/) | Pilot control crosswalks (not certification) |

Default agent workflow: install the CLI, run `aesa scan` / `aesa vet`, read
`findings.json`. Use this kit only for human-led deep review.
