# Using AESA Guard

AESA Guard is an **evidence-first security intelligence toolkit** for AI-agent ecosystems: deterministic discovery and security rules, a versioned assessment procedure, specialized modules, report schemas, CI gating, and an optional AI auditor skill.

Release **3.3.1** centers on **`aesa scan`**. Profile-based `aesa audit` remains for agent handoff packages. AESA is **not** a certification authority. Deterministic findings are `OBSERVED`/`POTENTIAL` evidence observations classified as capability, exposure, or security finding; judgment belongs to a human-authorized reviewer.

| Doc | Role |
| --- | --- |
| [`DOCUMENTATION-INDEX.md`](DOCUMENTATION-INDEX.md) | Full documentation map |
| [`GUARD-SCAN.md`](GUARD-SCAN.md) | Scan pipeline and artifacts |
| [`CLI-REFERENCE.md`](CLI-REFERENCE.md) | Every CLI command |
| [`AESA-GATE.md`](AESA-GATE.md) | Short product primer |
| [`AESA-3.0-PRODUCT-SPEC.md`](AESA-3.0-PRODUCT-SPEC.md) | Normative product contract (3.0 + Guard notes) |
| [`MIGRATION-3.1.md`](MIGRATION-3.1.md) | Upgrade from 3.0 |

---

## 1. Choose your scope

Fill audit inputs in Section 2 of [`../prompts/01-core-prompt.md`](../prompts/01-core-prompt.md). At minimum:

| Input | Why it matters |
| --- | --- |
| `REPOSITORY_URL` / local path | Exact repository under review |
| `KIT_DIR` / `WORK_DIR` | Read-only kit vs writable outputs (outside target clone) |
| `AUDIT_SCOPE_MODE` | Inventory-only vs selected/batch/full deep audit |
| `EXTERNAL_SOURCE_SCOPE` | Whether linked repos may be inspected |
| `HOST_AGENT` / host config | Integration trust depends on the host |
| `DATA_SENSITIVITY` | Blocks sensitive-production approval without evidence |

**Rule:** a URL inside a catalog is not authorization to audit that target.

---

## 2. First run (recommended) — Guard scan

### Option A — local uv

```bash
cd tools && uv sync --locked
uv run aesa scan /path/to/target -o /path/to/work/aesa-out
uv run aesa explain F-001 -o /path/to/work/aesa-out
uv run aesa baseline save -o /path/to/work/aesa-out
```

### Option B — Docker + AI agent

```bash
docker compose build
TARGET=/path/to/target-repo docker compose run --rm aesa \
  scan /work -o /work/aesa-out
```

Full guide: [`docker-agent-audit.md`](docker-agent-audit.md).

Outputs: `findings.json`, `findings.sarif.json`, `inventory.json`, `ecosystem-graph.json`, `scan-summary.txt`, `scan-report.md`, `profile.json`.

Then attach [`../skills/aesa-auditor/SKILL.md`](../skills/aesa-auditor/SKILL.md) and [`../prompts/04-passive-guardrails.md`](../prompts/04-passive-guardrails.md) for optional deep review.

### Option C — audit profiles (handoff package)

```bash
uv run aesa audit /path/to/target --profile quick|standard|deployment
```

| Profile | When |
| --- | --- |
| `quick` | Inventory + prioritization handoff |
| `standard` | Typical deep-review package |
| `deployment` | Adds deployment suitability worksheet |

---

## 3. Load the procedure (kit layout)

1. Operators: [`../prompts/00-OPERATOR-GUIDE.md`](../prompts/00-OPERATOR-GUIDE.md).
2. Attach [`../prompts/04-passive-guardrails.md`](../prompts/04-passive-guardrails.md) + [`../prompts/01-core-prompt.md`](../prompts/01-core-prompt.md).
3. Set `KIT_DIR` / `WORK_DIR`.
4. Before deep audit, attach [`../prompts/02-modules.md`](../prompts/02-modules.md) and only matching [`../modules/`](../modules/) (see [`../modules/README.md`](../modules/README.md)).
5. JSON contract: [`../prompts/03-report-contract.md`](../prompts/03-report-contract.md).
6. Emit structured claims; validate with `aesa validate claim` ([`EVIDENCE-MODEL.md`](EVIDENCE-MODEL.md)).

Monolith: [`../prompts/audit.full.md`](../prompts/audit.full.md). Index: [`../prompts/audit.md`](../prompts/audit.md).

### Module map (quick)

| Discovered type | Module |
| --- | --- |
| MCP | `modules/mcp.md` |
| Skill | `modules/skills.md` |
| Plugin | `modules/plugins.md` |
| Hook | `modules/hooks.md` |
| Subagent | `modules/subagents.md` |
| Automation / Workflow | `modules/automations.md` (+ `ci-cd.md` for GitHub Actions) |
| A2A | `modules/a2a.md` |
| Multimodal | `modules/multimodal.md` |
| Host integration | `modules/agent-host.md` |
| Memory / RAG | `modules/memory-rag.md` |
| Models | `modules/models-providers.md` |
| Browser agents | `modules/browser-agents.md` |

Threat backbone: [`threat-scenarios.md`](threat-scenarios.md). Rules: [`SECURITY-RULES.md`](SECURITY-RULES.md).

---

## 4. Keep evidence classes separate

Never upgrade one into another without new evidence:

- `SOURCE_STATIC`
- `ARTIFACT`
- `PROVENANCE`
- `HOST_CONFIGURATION`
- `RUNTIME`
- `EXTERNAL_INTELLIGENCE`
- `USER_ASSERTION`

Prefer `INSUFFICIENT EVIDENCE` / `NOT VERIFIED` over unsupported assurance. Full model: [`EVIDENCE-MODEL.md`](EVIDENCE-MODEL.md).

---

## 5. Produce outputs

### From Guard scan (automatic)

Terminal report + `findings.json` + SARIF + inventory + graph seed.

### From deep review (agent/human)

1. Narrative Markdown report (English)
2. Machine-readable summary conforming to [`../schemas/audit-report.schema.json`](../schemas/audit-report.schema.json)
3. Optional ecosystem graph refinements + digest manifest
4. Validate: `aesa validate report` / `aesa validate graph`

---

## 6. Continuous use / CI

```bash
aesa scan . --baseline aesa-out/baseline.json --fail-on high
aesa diff risk aesa-out/baseline.json aesa-out/findings.json
```

Consumer Action example: [`aesa-consumer-gate.example.yml`](aesa-consumer-gate.example.yml).

| Mode | Typical completion |
| --- | --- |
| Catalog / awesome-list URL | Stages 0–2 + Guard scan inventory |
| Authorized component sources | Stages 0–5+ as evidence allows |
| Host + production context | Full chain through Stage 8 + deployment worksheet |

---

## 7. Tooling command cheat sheet

Full detail: [`CLI-REFERENCE.md`](CLI-REFERENCE.md) and [`../tools/README.md`](../tools/README.md).

```bash
aesa scan PATH
aesa explain F-001 -o aesa-out
aesa baseline save -o aesa-out
aesa audit PATH --profile quick|standard|deployment
aesa inventory PATH
aesa validate report|graph|claim …
aesa diff report|graph|risk …
aesa export sarif …
aesa corpus run
aesa benchmark run
```
