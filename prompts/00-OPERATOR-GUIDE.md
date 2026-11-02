# Operator guide: AESA Kit v1.0

## What is in the kit

| File | Role |
|---|---|
| `01-core-prompt.md` | Main procedure (Sections 0–9, 11–21, 24–25). Give this to the audit agent; fill Section 2 inputs. |
| `02-modules.md` | Component-type modules (Skill, MCP, Plugin, …). Load **only** what applies. |
| `../modules/*.md` | Deep checklists for the six primary types (MCP, Skill, Plugin, Hook, Subagent, Automation). |
| `03-report-contract.md` | JSON templates, enums, output files, schema references. |
| `04-passive-guardrails.md` | **Required:** non-execution, anti-injection, `KIT_DIR`/`WORK_DIR`, worker rules. |
| `../schemas/*.json` | Official JSON Schema for `security-audit-summary.json`. |
| `../examples/*` | Sample context, inventory, and summary. |
| `audit.full.md` | Full monolithic procedure (single-file alternative to the split kit). |

## Difference from Audit Kit v5

AESA targets **agent ecosystems** (Skills, MCP, Hooks, …), not generic automated repo scanning. This kit has **no scanners or score script**; audits are **passive and read-only**. A secure environment (VM, restricted egress, no secrets) is still recommended—the prompt is not a technical sandbox.

## Environment prerequisites

1. **No secrets** in the agent environment: no SSH keys, cloud credentials, or production env vars.
2. **Restricted egress** if the agent has network access; only hosts allowed in scope.
3. **Read-only kit** — `KIT_DIR` = path to `prompts/` (or a read-only copy). Never clone the audit target into `KIT_DIR`.
4. **Writable `WORK_DIR`** — clones, reports, JSON, and state **outside** the target repo (e.g. `/audit/work`).
5. **GitHub token** read-only only, preferably via a secure integration—never paste tokens in chat.
6. **Guardrails:** the agent must load `04-passive-guardrails.md` at audit start; give subagents **Section 1** verbatim.

## Execution steps

1. Read this file and, if needed, [`../docs/usage.md`](../docs/usage.md).
2. Provide `04-passive-guardrails.md` and `01-core-prompt.md` to the audit agent. Fill Section 2: at minimum `REPOSITORY_URL`, `KIT_DIR`, `WORK_DIR`, `AUDIT_SCOPE_MODE`, `EXTERNAL_SOURCE_SCOPE`, `DATA_SENSITIVITY`, and host context.
3. The agent completes stages 0–2 (scope, discovery, triage). **Before Phase 4 deep audit**, attach `02-modules.md` and the needed files from `modules/`.
4. Narrative report per Section 21; JSON per `03-report-contract.md` and the schema.
5. For large repos/catalogs: batch with `COMPONENT_BATCH_SIZE` and `audit-state.json` across sessions.

## Module map

| Discovered | Load |
|---|---|
| MCP Server / Client | `modules/mcp.md` |
| Skill / Skill Pack | `modules/skills.md` |
| Plugin / Connector | `modules/plugins.md` |
| Hook | `modules/hooks.md` |
| Subagent | `modules/subagents.md` |
| Automation / scheduled workflow | `modules/automations.md` |
| Rule, RAG, model, IDE extension, … | Sections 10.2–10.15 in `02-modules.md` |

## Honest limitations

- AESA is **not** an automated scanner, sandbox, or penetration test.
- Default `score` is **null**; do not invent numeric scores.
- `recommend_production_use` is true only when production gates actually pass.
- A catalog link is **not** authorization to audit an external repo.

## Four separate questions

1. **Discovery** — What does the repo contain or reference?
2. **Component trust** — Is each in-scope source/artifact acceptable?
3. **Integration trust** — Is host connection bounded by identity and permissions?
4. **Production suitability** — Is the deployment acceptable for declared data sensitivity?

A positive answer to one does not imply the others.
