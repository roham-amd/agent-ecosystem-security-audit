# Using AESA

AESA is a **security audit framework** for AI agent ecosystems. It gives you a versioned procedure, specialized modules, and a report schema so different teams can produce comparable, evidence-bounded assessments.

It is **not** an automated scanner. You (or an audit agent following the procedure) perform a **passive, read-only** assessment within an explicitly authorized scope.

## 1. Choose your scope

Fill the audit inputs in Section 2 of [`prompts/v1/audit.md`](../prompts/v1/audit.md). At minimum:

| Input | Why it matters |
| --- | --- |
| `REPOSITORY_URL` | Exact GitHub repository under review |
| `AUDIT_SCOPE_MODE` | Inventory-only vs selected/batch/full deep audit |
| `EXTERNAL_SOURCE_SCOPE` | Whether linked repos may be inspected |
| `HOST_AGENT` / host config | Integration trust depends on the host |
| `DATA_SENSITIVITY` | Blocks sensitive-production approval without evidence |

**Rule:** a URL inside a catalog is not authorization to audit that target.

## 2. Load the procedure

1. Open [`prompts/v1/audit.md`](../prompts/v1/audit.md).
2. Provide it as the system/developer procedure to your audit agent, **or** follow it manually as a human auditor.
3. Attach only the specialized modules that match discovered component types from [`modules/`](../modules/).

Suggested module mapping:

| Discovered type | Module |
| --- | --- |
| MCP Server / Client | `modules/mcp.md` |
| Skill / Skill Pack | `modules/skills.md` |
| Plugin / Connector / Extension | `modules/plugins.md` |
| Hook / lifecycle handler | `modules/hooks.md` |
| Subagent / multi-agent | `modules/subagents.md` |
| Automation / Workflow | `modules/automations.md` |

## 3. Follow staged workflow

Complete stages in order. Do not silently skip.

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

Narrative report structure: Section 21 of the procedure (Persian by default; technical identifiers in English).

Machine-readable summary:

- Conform to [`schemas/audit-report.schema.json`](../schemas/audit-report.schema.json) (alias: [`schemas/AI_Agent_Ecosystem_Security_Audit_v1.schema.json`](../schemas/AI_Agent_Ecosystem_Security_Audit_v1.schema.json), the canonical filename named in v1.0 Section 22.5)
- Keep `score` as `null` and `score_type` as `NONE`
- Keep `recommend_production_use` as `false` unless all applicable production gates actually pass
- Set `json_validation_status` to `VALIDATED` only after a real validator run

Example starter inputs:

- [`examples/sample-audit-context.yaml`](../examples/sample-audit-context.yaml)
- [`examples/sample-component-inventory.json`](../examples/sample-component-inventory.json)

## 6. Passive-audit hard stops

During a passive AESA audit, do **not**:

- Execute Skills, Hooks, Plugins, MCP servers, Automations, Workflows, or repo scripts
- Install target dependencies (`npm install`, `pip install`, etc.)
- Contact operational endpoints or validate credentials
- Request or paste production secrets into chat
- Claim sandbox/scanner/SBOM/runtime results that were not performed

## 7. Sensitive production gate

For Confidential / Restricted / Regulated / personal / credential / financial / health data:

- Source review alone is **not** production validation
- Missing material runtime/host evidence → production suitability = `INSUFFICIENT EVIDENCE`
- `APPROVED_FOR_RESTRICTED_USE` must name allowed/prohibited data, enforcement points, owner, and expiry

## 8. Cite the exact version

Always record:

- AESA project / package version (`1.0.0`)
- Procedure version (`1.0`)
- Repository tag/commit of AESA used
- Audit date (UTC)
- Target repository commit/tree SHA (or explicit unavailability)
