# Using AESA

AESA is an **evidence-first security assessment toolkit** for AI agent ecosystems: a versioned procedure, specialized modules, report schemas, and deterministic local tooling.

Release **3.0.0** centers on `aesa audit` (Quick / Standard / Deployment profiles). It is **not** an automated scanner or certification authority. Judgment still belongs to a human-authorized AI auditor following the procedure.

Normative product contract: [`AESA-3.0-PRODUCT-SPEC.md`](AESA-3.0-PRODUCT-SPEC.md). Short primer: [`AESA-GATE.md`](AESA-GATE.md).

## 1. Choose your scope

Fill the audit inputs in Section 2 of [`prompts/01-core-prompt.md`](../prompts/01-core-prompt.md). At minimum:

| Input | Why it matters |
| --- | --- |
| `REPOSITORY_URL` | Exact repository under review |
| `KIT_DIR` / `WORK_DIR` | Read-only kit vs writable outputs (outside target clone) |
| `AUDIT_SCOPE_MODE` | Inventory-only vs selected/batch/full deep audit |
| `EXTERNAL_SOURCE_SCOPE` | Whether linked repos may be inspected |
| `HOST_AGENT` / host config | Integration trust depends on the host |
| `DATA_SENSITIVITY` | Blocks sensitive-production approval without evidence |

**Rule:** a URL inside a catalog is not authorization to audit that target.

## 2. First run (recommended)

### Option A — local uv

```bash
cd tools && uv sync --locked
uv run aesa audit /path/to/target --profile quick
# deepen:
uv run aesa audit /path/to/target --profile standard
```

### Option B — Docker + AI agent (Cursor, Claude Code, Codex, Antigravity, …)

No local Python required for discovery. See the full guide:
[`docker-agent-audit.md`](docker-agent-audit.md).

```bash
docker compose build
TARGET=/path/to/target-repo docker compose run --rm aesa \
  audit /work --profile standard -o /work/aesa-out
```

Then open your AI agent on the AESA kit + target, attach
[`skills/aesa-auditor/SKILL.md`](../skills/aesa-auditor/SKILL.md) and
[`prompts/04-passive-guardrails.md`](../prompts/04-passive-guardrails.md), and point it at
`aesa-out/audit-context.md` / `inventory.json`.

Outputs under `aesa-out/`: `inventory.json`, `ecosystem-graph.json`, `audit-context.md`, `profile.json`.

Then attach [`skills/aesa-auditor/SKILL.md`](../skills/aesa-auditor/SKILL.md) (or the prompt kit) and load only modules listed in the handoff.

## 3. Load the procedure (kit layout)

1. Operators: read [`prompts/00-OPERATOR-GUIDE.md`](../prompts/00-OPERATOR-GUIDE.md).
2. Attach [`prompts/04-passive-guardrails.md`](../prompts/04-passive-guardrails.md) and provide [`prompts/01-core-prompt.md`](../prompts/01-core-prompt.md).
3. Set `KIT_DIR` / `WORK_DIR` in Section 2.8.
4. Before component deep audit, attach [`prompts/02-modules.md`](../prompts/02-modules.md) and only matching [`modules/`](../modules/).
5. JSON contract: [`prompts/03-report-contract.md`](../prompts/03-report-contract.md).

Monolithic copy (optional): [`prompts/audit.full.md`](../prompts/audit.full.md). Index: [`prompts/audit.md`](../prompts/audit.md).

| Discovered type | Module |
| --- | --- |
| MCP Server / Client | `modules/mcp.md` |
| Skill / Skill Pack | `modules/skills.md` |
| Plugin / Connector / Extension | `modules/plugins.md` |
| Hook / lifecycle handler | `modules/hooks.md` |
| Subagent / multi-agent | `modules/subagents.md` |
| Automation / Workflow / CI | `modules/automations.md` |
| A2A / Agent Card | `modules/a2a.md` |
| Multimodal pipelines | `modules/multimodal.md` |

### Tooling commands (3.0+)

```bash
aesa audit PATH --profile quick|standard|deployment
aesa preflight PATH          # alias of audit --profile quick
aesa inventory PATH
aesa validate report summary.json
aesa validate graph graph.json
aesa diff report old.json new.json
aesa export sarif report.json
aesa corpus run              # tooling fixtures
aesa benchmark run           # detection benchmark scaffold (no LLM yet)
```

See [`tools/README.md`](../tools/README.md) and [`MIGRATION-2.0.md`](MIGRATION-2.0.md).

| If you only have… | Complete at least… | Typical ecosystem decision |
| --- | --- | --- |
| A catalog / awesome-list URL | Stages 0–2 | `ECOSYSTEM_INVENTORY_ONLY` |
| Authorized component sources | Stages 0–5+ as evidence allows | Per-component decisions |
| Host + production context + staging evidence | Full chain through Stage 8 | Possible production suitability decisions |

## 4. Keep evidence classes separate

Never upgrade one into another without new evidence:

- `SOURCE_STATIC`
- `ARTIFACT`
- `PROVENANCE`
- `HOST_CONFIGURATION`
- `RUNTIME`
- `EXTERNAL_INTELLIGENCE`
- `USER_ASSERTION`

Prefer `INSUFFICIENT EVIDENCE` over unsupported assurance.

## 5. Produce outputs

1. Narrative Markdown report
2. Machine-readable summary conforming to [`schemas/audit-report.schema.json`](../schemas/audit-report.schema.json)
3. Optional ecosystem graph + digest manifest
4. Validate: `aesa validate report`

## 6. Continuous use

- Save `aesa-out/inventory.json` as a baseline
- Diff with `aesa diff` or the consumer Action example in [`aesa-consumer-gate.example.yml`](aesa-consumer-gate.example.yml)
