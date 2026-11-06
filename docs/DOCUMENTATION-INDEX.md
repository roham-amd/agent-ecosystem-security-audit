# authdiff documentation index

Complete map of project documentation for **authdiff 3.6.0** (Authority Diff;
procedure **1.0**, tooling **0.9.0**, rule pack **1.4**). The `aesa` CLI name
remains a compatibility alias.

Use this file as the table of contents. Prefer the **primary** doc for each topic; secondary docs add depth or history.

---

## Start here

| Audience | Read first | Then |
| --- | --- | --- |
| New operator | [`../README.md`](../README.md) | [`INSTALL.md`](INSTALL.md), [`GUARD-SCAN.md`](GUARD-SCAN.md) |
| CLI / DevSecOps | [`CLI-REFERENCE.md`](CLI-REFERENCE.md) | [`../tools/README.md`](../tools/README.md), [`AESA-GATE.md`](AESA-GATE.md), [`POLICY.md`](POLICY.md) |
| AI coding agent | [`../skills/aesa-auditor/SKILL.md`](../skills/aesa-auditor/SKILL.md) | [`../archive/methodology/prompts/04-passive-guardrails.md`](../archive/methodology/prompts/04-passive-guardrails.md) |
| Security reviewer | [`EVIDENCE-MODEL.md`](EVIDENCE-MODEL.md) | [`SECURITY-RULES.md`](SECURITY-RULES.md), [`threat-scenarios.md`](threat-scenarios.md) |
| Contributor | [`../CONTRIBUTING.md`](../CONTRIBUTING.md) | [`architecture/`](architecture/), [`engineering-plan.md`](engineering-plan.md) |
| Security contact | [`../SECURITY.md`](../SECURITY.md) | [`toolchain-threat-model.md`](toolchain-threat-model.md) |

---

## Product and positioning

| Document | Contents |
| --- | --- |
| [`../README.md`](../README.md) | Authority Diff identity: doctor → open → init → scan |
| [`AESA-GATE.md`](AESA-GATE.md) | Short primer: discover / assess / govern |
| [`GUARD-3.6-BACKLOG.md`](GUARD-3.6-BACKLOG.md) | **Current** Authority Diff backlog |
| [`RADICAL-ALTERNATIVES.md`](RADICAL-ALTERNATIVES.md) | Broker / attack-replay / AUTHORITY LSP MVPs |
| [`LEGACY-METHODOLOGY.md`](LEGACY-METHODOLOGY.md) | Archived prompts/modules location |
| [`atlas/README.md`](atlas/README.md) | Ecosystem Atlas precision program |
| [`../archive/methodology/`](../archive/methodology/) | Optional methodology kit (not the product path) |
| [`../examples/demo-vulnerable/`](../examples/demo-vulnerable/) | Seeded Authority Diff demo repo |
| [`GUARD-3.4-BACKLOG.md`](GUARD-3.4-BACKLOG.md) | Historical 3.4 productization backlog |
| [`POLICY.md`](POLICY.md) | `.aesa.yml` policy contract + CI trusted-policy |
| [`COVERAGE-MATRIX.md`](COVERAGE-MATRIX.md) | Automated vs manual coverage |
| [`AESA-3.0-PRODUCT-SPEC.md`](AESA-3.0-PRODUCT-SPEC.md) | Normative 3.0 product contract (historical) |
| [`GUARD-SCAN.md`](GUARD-SCAN.md) | `aesa scan` end-to-end: artifacts, baselines, Action |
| [`MIGRATION-2.0.md`](MIGRATION-2.0.md) | 1.x → 2.x migration |
| [`MIGRATION-3.1.md`](MIGRATION-3.1.md) | 3.0 → 3.1 Guard migration |
| [`../CHANGELOG.md`](../CHANGELOG.md) | Release history |
| [`../VERSION`](../VERSION) | Authoritative product version string |
| [`../canonical/versions.json`](../canonical/versions.json) | Product, schemas, corpus, benchmark, tooling tags |
| [`../canonical/release-manifest.json`](../canonical/release-manifest.json) | North-star + interface matrix |

---

## Operator how-to

| Document | Contents |
| --- | --- |
| [`usage.md`](usage.md) | Scope, doctor/vet/scan, kit load order, continuous use |
| [`CLI-REFERENCE.md`](CLI-REFERENCE.md) | Every `aesa` command, flags, exit codes, examples |
| [`INSTALL.md`](INSTALL.md) | `uv tool install` / PyPI / clone install |
| [`../tools/README.md`](../tools/README.md) | Install (uv), Docker, quality gates, package layout |
| [`pilots/README.md`](pilots/README.md) | Pilot-repository scan harness |
| [`INTAKE-CHANNEL.md`](INTAKE-CHANNEL.md) | AgentSecBench external intake (N tracking) |
| [`docker-agent-audit.md`](docker-agent-audit.md) | Docker discovery + Cursor / Claude / Codex deep review |
| [`aesa-consumer-gate.example.yml`](aesa-consumer-gate.example.yml) | Example GitHub Actions consumer workflow (trusted-policy) |
| [`recipes/README.md`](recipes/README.md) | Scenario recipes index |
| [`recipes/guard-first-assessment.md`](recipes/guard-first-assessment.md) | Default Authority Diff first assessment |
| [`recipes/catalog-inventory.md`](recipes/catalog-inventory.md) | Awesome-list / catalog inventory |
| [`recipes/small-repo-deep-audit.md`](recipes/small-repo-deep-audit.md) | Small repo deep assessment |
| [`recipes/source-only-review.md`](recipes/source-only-review.md) | Source-only constraints |
| [`recipes/staging-boundary.md`](recipes/staging-boundary.md) | Staging / runtime authorization boundary |

---

## Security methodology

| Document | Contents |
| --- | --- |
| [`../archive/methodology/prompts/00-OPERATOR-GUIDE.md`](../archive/methodology/prompts/00-OPERATOR-GUIDE.md) | Kit contents, environment, execution steps |
| [`../archive/methodology/prompts/01-core-prompt.md`](../archive/methodology/prompts/01-core-prompt.md) | Full audit procedure (stages, inputs, report sections) |
| [`../archive/methodology/prompts/02-modules.md`](../archive/methodology/prompts/02-modules.md) | Module index summaries |
| [`../archive/methodology/prompts/03-report-contract.md`](../archive/methodology/prompts/03-report-contract.md) | JSON report contract and enums |
| [`../archive/methodology/prompts/04-passive-guardrails.md`](../archive/methodology/prompts/04-passive-guardrails.md) | Mandatory passive-audit safety rules |
| [`../archive/methodology/prompts/audit.md`](../archive/methodology/prompts/audit.md) | Kit entry pointer |
| [`../archive/methodology/prompts/scan-triage.md`](../archive/methodology/prompts/scan-triage.md) | Lightweight scan + triage (default agent path) |
| [`../archive/methodology/prompts/audit.full.md`](../archive/methodology/prompts/audit.full.md) | Generated monolithic procedure |
| [`EVIDENCE-MODEL.md`](EVIDENCE-MODEL.md) | Evidence classes, findings, claims, capabilities, strength |
| [`SECURITY-RULES.md`](SECURITY-RULES.md) | Deterministic Guard rules AESA-RULE-001…016 |
| [`threat-scenarios.md`](threat-scenarios.md) | Capability-first threat scenarios |
| [`toolchain-threat-model.md`](toolchain-threat-model.md) | Threats against AESA itself |
| [`runtime-validation/README.md`](runtime-validation/README.md) | Runtime validation status (design only; disabled by default) |
| [`runtime-validation/ARCHITECTURE.md`](runtime-validation/ARCHITECTURE.md) | Runtime orchestrator boundaries and activation contract |
| [`runtime-validation/THREAT-MODEL.md`](runtime-validation/THREAT-MODEL.md) | Runtime validation adversaries and controls |
| [`hosts/README.md`](hosts/README.md) | Host profiles: declared vs effective permissions |
| [`hosts/cursor.md`](hosts/cursor.md) | Cursor host profile |
| [`hosts/claude-code.md`](hosts/claude-code.md) | Claude Code host profile |
| [`../archive/methodology/control-packs/README.md`](../archive/methodology/control-packs/README.md) | Control crosswalk packs (pilot) |

---

## Specialized modules

| Document | Contents |
| --- | --- |
| [`../archive/methodology/modules/README.md`](../archive/methodology/modules/README.md) | Module index and when to load each |
| [`../archive/methodology/modules/mcp.md`](../archive/methodology/modules/mcp.md) | MCP servers / clients |
| [`../archive/methodology/modules/skills.md`](../archive/methodology/modules/skills.md) | Skills and skill packs |
| [`../archive/methodology/modules/plugins.md`](../archive/methodology/modules/plugins.md) | Plugins / connectors |
| [`../archive/methodology/modules/hooks.md`](../archive/methodology/modules/hooks.md) | Hooks / lifecycle handlers |
| [`../archive/methodology/modules/subagents.md`](../archive/methodology/modules/subagents.md) | Subagents / multi-agent |
| [`../archive/methodology/modules/automations.md`](../archive/methodology/modules/automations.md) | Automations / scheduled tasks |
| [`../archive/methodology/modules/a2a.md`](../archive/methodology/modules/a2a.md) | Agent-to-Agent / Agent Cards |
| [`../archive/methodology/modules/multimodal.md`](../archive/methodology/modules/multimodal.md) | Multimodal / cross-modal |
| [`../archive/methodology/modules/agent-host.md`](../archive/methodology/modules/agent-host.md) | Agent host integration |
| [`../archive/methodology/modules/memory-rag.md`](../archive/methodology/modules/memory-rag.md) | Memory / RAG |
| [`../archive/methodology/modules/models-providers.md`](../archive/methodology/modules/models-providers.md) | Models / providers |
| [`../archive/methodology/modules/browser-agents.md`](../archive/methodology/modules/browser-agents.md) | Browser agents |
| [`../archive/methodology/modules/ci-cd.md`](../archive/methodology/modules/ci-cd.md) | CI/CD surfaces |

---

## Architecture and engineering

| Document | Contents |
| --- | --- |
| [`engineering-plan.md`](engineering-plan.md) | Milestone status through 3.5 Authority Diff |
| [`architecture/ADR-001-canonical-sources.md`](architecture/ADR-001-canonical-sources.md) | Canonical version/schema sources |
| [`architecture/ADR-002-semantic-validation.md`](architecture/ADR-002-semantic-validation.md) | Semantic validation |
| [`architecture/ADR-003-monolith-generation.md`](architecture/ADR-003-monolith-generation.md) | Prompt monolith generation |
| [`architecture/ADR-004-gating-and-policy.md`](architecture/ADR-004-gating-and-policy.md) | Gate classes + trusted policy |

---

## Examples and schemas

| Document | Contents |
| --- | --- |
| [`../examples/guard-scan/`](../examples/guard-scan/) | Sample Guard scan artifacts |
| [`../examples/aesa.policy.example.yml`](../examples/aesa.policy.example.yml) | Sample `.aesa.yml` |
| [`../schemas/README.md`](../schemas/README.md) | Published JSON Schemas |
| [`../tests/rules/README.md`](../tests/rules/README.md) | Rule-quality fixture pack |
