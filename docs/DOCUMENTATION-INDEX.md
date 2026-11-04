# AESA documentation index

Complete map of project documentation for **AESA Guard 3.4.0** (procedure **1.0**, tooling **0.7.0**).

Use this file as the table of contents. Prefer the **primary** doc for each topic; secondary docs add depth or history.

---

## Start here

| Audience | Read first | Then |
| --- | --- | --- |
| New operator | [`../README.md`](../README.md) | [`usage.md`](usage.md), [`GUARD-SCAN.md`](GUARD-SCAN.md) |
| CLI / DevSecOps | [`CLI-REFERENCE.md`](CLI-REFERENCE.md) | [`../tools/README.md`](../tools/README.md), [`AESA-GATE.md`](AESA-GATE.md) |
| AI coding agent | [`../skills/aesa-auditor/SKILL.md`](../skills/aesa-auditor/SKILL.md) | [`../prompts/04-passive-guardrails.md`](../prompts/04-passive-guardrails.md) |
| Security reviewer | [`EVIDENCE-MODEL.md`](EVIDENCE-MODEL.md) | [`SECURITY-RULES.md`](SECURITY-RULES.md), [`threat-scenarios.md`](threat-scenarios.md) |
| Contributor | [`../CONTRIBUTING.md`](../CONTRIBUTING.md) | [`architecture/`](architecture/), [`engineering-plan.md`](engineering-plan.md) |
| Security contact | [`../SECURITY.md`](../SECURITY.md) | [`toolchain-threat-model.md`](toolchain-threat-model.md) |

---

## Product and positioning

| Document | Contents |
| --- | --- |
| [`../README.md`](../README.md) | Product identity, first experience, layout, principles, versioning |
| [`AESA-GATE.md`](AESA-GATE.md) | Short Guard primer: discover / assess / govern |
| [`GUARD-3.4-BACKLOG.md`](GUARD-3.4-BACKLOG.md) | 3.4 productization backlog and acceptance criteria |
| [`POLICY.md`](POLICY.md) | `.aesa.yml` policy contract |
| [`COVERAGE-MATRIX.md`](COVERAGE-MATRIX.md) | Automated vs manual coverage |
| [`AESA-3.0-PRODUCT-SPEC.md`](AESA-3.0-PRODUCT-SPEC.md) | Normative 3.0 product contract (Guard UX added in 3.1) |
| [`GUARD-SCAN.md`](GUARD-SCAN.md) | `aesa scan` end-to-end: artifacts, profiles vs scan, baselines |
| [`MIGRATION-2.0.md`](MIGRATION-2.0.md) | 1.x → 2.x migration |
| [`MIGRATION-3.1.md`](MIGRATION-3.1.md) | 3.0 → 3.1 Guard migration |
| [`../CHANGELOG.md`](../CHANGELOG.md) | Release history |
| [`../VERSION`](../VERSION) | Authoritative product version string |
| [`../canonical/versions.json`](../canonical/versions.json) | Product, schemas, corpus, benchmark, tooling tags |

---

## Operator how-to

| Document | Contents |
| --- | --- |
| [`usage.md`](usage.md) | Scope, Guard scan, audit profiles, kit load order, continuous use |
| [`CLI-REFERENCE.md`](CLI-REFERENCE.md) | Every `aesa` command, flags, exit codes, examples |
| [`INSTALL.md`](INSTALL.md) | `uv tool install` / PyPI / clone install |
| [`../tools/README.md`](../tools/README.md) | Install (uv), Docker, quality gates, package layout |
| [`pilots/README.md`](pilots/README.md) | Pilot-repository scan harness |
| [`INTAKE-CHANNEL.md`](INTAKE-CHANNEL.md) | AgentSecBench external intake (N tracking) |
| [`docker-agent-audit.md`](docker-agent-audit.md) | Docker discovery + Cursor / Claude / Codex deep review |
| [`aesa-consumer-gate.example.yml`](aesa-consumer-gate.example.yml) | Example GitHub Actions consumer workflow |
| [`recipes/README.md`](recipes/README.md) | Scenario recipes index |
| [`recipes/catalog-inventory.md`](recipes/catalog-inventory.md) | Awesome-list / catalog inventory |
| [`recipes/small-repo-deep-audit.md`](recipes/small-repo-deep-audit.md) | Small repo deep assessment |
| [`recipes/source-only-review.md`](recipes/source-only-review.md) | Source-only constraints |
| [`recipes/staging-boundary.md`](recipes/staging-boundary.md) | Staging / runtime authorization boundary |
| [`recipes/guard-first-assessment.md`](recipes/guard-first-assessment.md) | Default Guard-first assessment recipe |

---

## Security methodology

| Document | Contents |
| --- | --- |
| [`../prompts/00-OPERATOR-GUIDE.md`](../prompts/00-OPERATOR-GUIDE.md) | Kit contents, environment, execution steps |
| [`../prompts/01-core-prompt.md`](../prompts/01-core-prompt.md) | Full audit procedure (stages, inputs, report sections) |
| [`../prompts/02-modules.md`](../prompts/02-modules.md) | Module index summaries |
| [`../prompts/03-report-contract.md`](../prompts/03-report-contract.md) | JSON report contract and enums |
| [`../prompts/04-passive-guardrails.md`](../prompts/04-passive-guardrails.md) | Mandatory passive-audit safety rules |
| [`../prompts/audit.md`](../prompts/audit.md) | Kit entry pointer |
| [`../prompts/scan-triage.md`](../prompts/scan-triage.md) | Lightweight scan + triage (default agent path) |
| [`../prompts/audit.full.md`](../prompts/audit.full.md) | Generated monolithic procedure |
| [`EVIDENCE-MODEL.md`](EVIDENCE-MODEL.md) | Evidence classes, findings, claims, capabilities |
| [`SECURITY-RULES.md`](SECURITY-RULES.md) | Deterministic Guard rules AESA-RULE-001…010 |
| [`threat-scenarios.md`](threat-scenarios.md) | Capability-first threat scenarios |
| [`toolchain-threat-model.md`](toolchain-threat-model.md) | Threats against AESA itself |
| [`runtime-validation/README.md`](runtime-validation/README.md) | Runtime validation status (design only; disabled by default) |
| [`runtime-validation/ARCHITECTURE.md`](runtime-validation/ARCHITECTURE.md) | Runtime orchestrator boundaries and activation contract |
| [`runtime-validation/THREAT-MODEL.md`](runtime-validation/THREAT-MODEL.md) | Runtime validation adversaries and controls |
| [`hosts/README.md`](hosts/README.md) | Host profiles: declared vs effective permissions |
| [`hosts/cursor.md`](hosts/cursor.md) | Cursor host profile |
| [`hosts/claude-code.md`](hosts/claude-code.md) | Claude Code host profile |
| [`../control-packs/README.md`](../control-packs/README.md) | Control crosswalk packs (pilot) |

---

## Specialized modules

| Document | Contents |
| --- | --- |
| [`../modules/README.md`](../modules/README.md) | Module index and when to load each |
| [`../modules/mcp.md`](../modules/mcp.md) | MCP servers / clients |
| [`../modules/skills.md`](../modules/skills.md) | Skills and skill packs |
| [`../modules/plugins.md`](../modules/plugins.md) | Plugins / connectors |
| [`../modules/hooks.md`](../modules/hooks.md) | Hooks / lifecycle handlers |
| [`../modules/subagents.md`](../modules/subagents.md) | Subagents / multi-agent |
| [`../modules/automations.md`](../modules/automations.md) | Automations / scheduled tasks |
| [`../modules/a2a.md`](../modules/a2a.md) | Agent-to-Agent / Agent Cards |
| [`../modules/multimodal.md`](../modules/multimodal.md) | Multimodal / cross-modal |
| [`../modules/agent-host.md`](../modules/agent-host.md) | Host agent security |
| [`../modules/memory-rag.md`](../modules/memory-rag.md) | Memory / RAG |
| [`../modules/models-providers.md`](../modules/models-providers.md) | Models / providers |
| [`../modules/browser-agents.md`](../modules/browser-agents.md) | Browser agents |
| [`../modules/ci-cd.md`](../modules/ci-cd.md) | CI/CD agent surfaces |

---

## Schemas and examples

| Document | Contents |
| --- | --- |
| [`../schemas/README.md`](../schemas/README.md) | Schema catalog and purpose |
| [`../schemas/audit-report.schema.json`](../schemas/audit-report.schema.json) | Audit report summary |
| [`../schemas/ecosystem-graph.schema.json`](../schemas/ecosystem-graph.schema.json) | Ecosystem graph |
| [`../schemas/audit-manifest.schema.json`](../schemas/audit-manifest.schema.json) | Audit engagement manifest |
| [`../schemas/audit-diff.schema.json`](../schemas/audit-diff.schema.json) | Report / graph diff |
| [`../schemas/evidence-digest-manifest.schema.json`](../schemas/evidence-digest-manifest.schema.json) | Digest manifest |
| [`../schemas/runtime-test-record.schema.json`](../schemas/runtime-test-record.schema.json) | Authorized runtime test record |
| [`../schemas/structured-claim.schema.json`](../schemas/structured-claim.schema.json) | AI auditor intermediate claims |
| [`../examples/`](../examples/) | Sample inventory, summary, context, runtime record |

Canonical report schema source: [`../canonical/schemas/audit-report.schema.json`](../canonical/schemas/audit-report.schema.json) (publish with `aesa build schemas`).

---

## Skills and Cursor integration

| Document | Contents |
| --- | --- |
| [`../skills/aesa-auditor/SKILL.md`](../skills/aesa-auditor/SKILL.md) | Canonical auditor skill (Guard-first) |
| [`../skills/cursor/AESA.md`](../skills/cursor/AESA.md) | Cursor task shortcuts |

---

## Testing and quality

| Document | Contents |
| --- | --- |
| [`../tests/corpus/README.md`](../tests/corpus/README.md) | Tooling regression corpus CORPUS-001…010 |
| [`../tests/benchmark/README.md`](../tests/benchmark/README.md) | AgentSecBench (detection expectations) |
| [`engineering-plan.md`](engineering-plan.md) | Milestone status vs roadmap |
| [`.github/actions/aesa-gate/action.yml`](../.github/actions/aesa-gate/action.yml) | Composite CI Action (Guard) |
| [`.github/workflows/aesa-validate.yml`](../.github/workflows/aesa-validate.yml) | Kit CI validation workflow |

---

## Architecture (ADRs)

| Document | Contents |
| --- | --- |
| [`architecture/ADR-001-canonical-sources.md`](architecture/ADR-001-canonical-sources.md) | Canonical schemas / versions |
| [`architecture/ADR-002-semantic-validation.md`](architecture/ADR-002-semantic-validation.md) | Semantic validation beyond JSON Schema |
| [`architecture/ADR-003-monolith-generation.md`](architecture/ADR-003-monolith-generation.md) | Prompt kit → `audit.full.md` |
| [`architecture/ADR-004-gating-and-policy.md`](architecture/ADR-004-gating-and-policy.md) | Gate classes, `.aesa.yml`, exit codes |

---

## Supply chain helpers

| Document | Contents |
| --- | --- |
| [`../tools/aesa/supply_chain/README.md`](../tools/aesa/supply_chain/README.md) | Digest verify / manifest helpers |

---

## Documentation rules

1. Narrative procedure and reports are **English**.
2. Do not document AESA as a certification authority or full vulnerability scanner.
3. Keep version tables synchronized with `VERSION` and `canonical/versions.json`.
4. When adding a CLI command, update `CLI-REFERENCE.md`, `tools/README.md`, and this index.
5. When adding a module, update `modules/README.md`, `prompts/02-modules.md`, and the auditor skill table.
