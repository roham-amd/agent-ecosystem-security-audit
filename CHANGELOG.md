# Changelog

All notable changes to the AESA framework are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses semantic versioning for packaged releases (`2.0.0`, …).
The included audit procedure version remains independently numbered (procedure **1.0** under `prompts/`).

## [3.3.1] — 2026-11-04

### Added

- Frozen AgentSecBench-LLM evaluation contract (`EVALUATION-CONTRACT-0.3.0.json`) and protocol.
- External intake vault: `aesa benchmark contract|intake|intakes|submitter-package`.
- Submitter package without ground truth; provenance classes (`external` / `pilot` / `sample` / `template`).
- Honest external evaluation report documenting **N = 0** genuine external submissions.
- `CANDIDATE-IMPROVEMENTS.md` for post-freeze feedback (no silent 0.3.0 edits).
- Outreach kit: `PARTICIPATION.md`, `OUTREACH.md`, `COLLECTION-CRITERIA.md`, collection funnel log.
- `aesa benchmark collection-status` — invitations ≠ responses ≠ valid intakes.
- Untrusted-intake hardening: size/file/findings limits, symlink rejection, no execution, invalid payloads not vault-written.

### Changed

- Product **3.3.1**; tooling **0.6.1**.
- Example submission relocated to `submissions/templates/` (not external evidence).

### Notes

- **N = 0** valid external intakes (correct until independent evidence arrives). Dataset **0.3.0** remains frozen.
- Live model invocation, IDE/MCP, SaaS remain deferred.
- Next meaningful achievement: first independent valid external intake.

## [3.3.0] — 2026-11-04

### Added

- Baseline contract **1.3**: same-path content changes classified as `components_modified` (not unrelated fingerprint remove+add); clone path expansion remains fingerprint-stable.
- AgentSecBench validation layer: dataset checksums, public/held-out splits, `aesa benchmark governance`, evaluation pins, offline `--report`.
- Independent review process + sample blind reviews/adjudications (`tests/benchmark/llm/reviews/`).
- External submission schema (`schemas/agentsecbench-submission.schema.json`) and external submitter guide.

### Changed

- Product **3.3.0**; tooling **0.6.0**; AgentSecBench-LLM dataset **0.3.0**.
- Explicit policy: no definitive leaderboard from eight cases / maintainer pilots.

### Notes

- IDE/MCP/hosted surfaces remain deferred.

## [3.2.1] — 2026-11-04

### Added

- Baseline contract **1.2**: fingerprint-first identity, path maps, rename/move detection without add/remove noise; finding keys prefer `rule_id:fingerprint`.
- Fingerprint/baseline integration tests (rename, move, duplicates, clones, genuine change).
- AgentSecBench-LLM **0.2.0**: eight reviewed ground-truth cases (positive / negative / ambiguous); dataset + rubric versions; multi-agent pilot submissions; separated detection / evidence / severity / unsupported-claim scores.

### Changed

- Product **3.2.1**; tooling **0.5.1**.
- IDE/MCP interfaces remain deferred until scan + benchmark interfaces stay stable.

### Notes

- Local complete; not a published shared release until committed/tagged/pushed.
- Offline LLM scoring is still not live model evaluation.

## [3.2.0] — 2026-11-04

### Added

- **Rule-quality pack** (`tests/rules/`, `aesa benchmark rules`): positive / negative / ambiguous fixtures for AESA-RULE-001…010 with finding-class and severity calibration checks; `--fail-on` gates ignore pure CAPABILITY observations.
- **AgentSecBench LLM runner** (`aesa benchmark llm`): model-agnostic offline scoring for precision, recall, evidence accuracy, severity calibration, and hallucinated claims; `--validate-only` for CI without submissions.
- **Host profiles** (`aesa hosts list|show`, adapter `host_profiles`): Cursor and Claude Code PARTIAL; GitHub Copilot MANUAL_ONLY; declared vs effective permissions explicit.
- Runtime validation **architecture** and **threat model** (`docs/runtime-validation/`); still disabled by default — no target execution in passive scan.

### Changed

- Product **3.2.0**; tooling **0.5.0**; AgentSecBench **0.3.0**; rule-quality pack **1.0.0**.
- Skill secret-hint detection ignores short negation windows (fixes “No credential handling” false positive).
- RULE-007 accepts `Automation / Workflow` and secret/credential hint aliases from CI adapters.

### Notes

- LLM runner never calls model providers.
- Runtime harness remains design-only.

## [3.1.1] — 2026-11-04

### Added

- Finding classes: `CAPABILITY`, `EXPOSURE`, `SECURITY_FINDING` — capability detection is no longer treated as a vulnerability by default.
- Capability `origin`: `DECLARED` / `POTENTIAL` / `TYPE_DEFAULT` / `EFFECTIVE` / `VERIFIED`.
- Evidence provenance on rule hits: `content_digest`, `source_commit`, `observed_at`, and line spans when locatable.
- Stable component `fingerprint` fields; baseline contract **1.1** with fingerprint-aware risk deltas.
- Authority-first terminal snapshot (components, authority, exposures, high-priority items, example path).
- Canonical [`release-manifest.json`](canonical/release-manifest.json) as the single public product contract.

### Changed

- Product version **3.1.1**; tooling package **0.4.1**; rule pack **1.1**.
- Rule severities recalibrated: local MCP / subagent / unattended / naming markers default to capability or exposure notes; HIGH/CRITICAL require exposure conditions (e.g. broad path args, env inheritance).
- `--fail-on high|any` ignores pure `CAPABILITY` observations.
- Findings contract **1.1** (`findings_version`).

### Notes

- AI deep assessment (`aesa audit` + auditor skill) remains optional.
- AgentSecBench LLM precision/recall runner is still deferred.

## [3.1.0] — 2026-11-04

### Added

- **AESA Guard** product identity: one-command `aesa scan` with terminal report, `findings.json`, SARIF, capabilities extraction, and versioned deterministic rules (`AESA-RULE-001`…`010`).
- `aesa explain`, `aesa baseline save|show`, `aesa diff risk`, `aesa validate claim`.
- Structured claim schema (`schemas/structured-claim.schema.json`) for AI auditor intermediate objects.
- Modules: agent-host, memory-rag, models-providers, browser-agents, ci-cd; threat scenario backbone (`docs/threat-scenarios.md`).
- AgentSecBench **0.2.0**: Guard rule expectations on BENCH fixtures (LLM scoring still deferred).
- CI Action hardening: inputs via env vars; `mode=scan|audit`; `--fail-on`; coverage report; SARIF note.
- Documentation suite: `docs/DOCUMENTATION-INDEX.md`, `GUARD-SCAN.md`, `CLI-REFERENCE.md`, `SECURITY-RULES.md`, `EVIDENCE-MODEL.md`, `MIGRATION-3.1.md`, `modules/README.md`, `schemas/README.md`; Guard-aligned README/usage/tools/operator guides.

### Changed

- Product version **3.1.0**; tooling package **0.4.0**.
- README / SECURITY / skill / Gate primer repositioned around Guard; supported release line **3.x**.
- Version hints in audit/SARIF resolve from `VERSION` / `canonical/versions.json` (no hard-coded 3.0.0 drift).

### Notes

- Report schema / procedure versions remain **1.0**.
- Guard findings are OBSERVED/POTENTIAL; incomplete coverage is never a clean bill of health.

## [3.0.1] — 2026-11-04

### Added

- Docker image + Compose (`Dockerfile`, `docker-compose.yml`) on digest-pinned `python:3.15.2-slim-trixie` and `ghcr.io/astral-sh/uv`.
- Operator guide [`docs/docker-agent-audit.md`](docs/docker-agent-audit.md) — Docker preflight + AI agent deep review (Cursor, Claude Code, Codex, Antigravity, …).
- Dev quality toolchain: mypy, pytest-cov, pip-audit; optional Ruff hooks via `.pre-commit-config.yaml` (`uvx pre-commit`).
- Dependabot `docker` ecosystem for `tag@digest` base updates; Actions remain SHA-pinned.
- `tools/.python-version` (`3.15`) and committed `tools/uv.lock`.

### Changed

- Product version **3.0.1**; tooling package **0.3.1**.
- Tooling stack: **uv + pyproject.toml + uv.lock + Ruff + Pytest + mypy** (PEP 735 `[dependency-groups]`; constraints via `uv add`; exact versions/hashes in lock). Removed `constraints.txt` / `requirements*.txt`.
- CI and AESA Gate install with `uv sync --locked` / `uv run --locked`; CI pins patch via `uv python install 3.15.2`.
- Production containers use `uv sync --locked --no-dev`.

### Notes

- Report schema / procedure versions remain **1.0** (no breaking report contract).

## [3.0.0] — 2026-11-03

### Added

- `aesa deps outdated` / `aesa deps upgrade` — ncu-style PyPI pin check and bump for constraints / lock / `pyproject.toml`.
- `aesa lint` — Ruff lint/format gate for `tools/aesa` + `tests`.
- Dependabot (`.github/dependabot.yml`): weekly grouped Python + `github-actions` updates.
- **AESA 3.0 product specification** ([`docs/AESA-3.0-PRODUCT-SPEC.md`](docs/AESA-3.0-PRODUCT-SPEC.md)): CLI contract, adapter architecture, evidence rules, 30-day backlog status.
- `aesa audit PATH --profile quick|standard|deployment` — unified local assessment entry (inventory + handoff package + profile metadata).
- Inventory adapter `github_workflows` for `.github/workflows` authority surfaces.
- Consumer composite Action [`.github/actions/aesa-gate`](.github/actions/aesa-gate) + example workflow ([`docs/aesa-consumer-gate.example.yml`](docs/aesa-consumer-gate.example.yml)).
- Agent detection benchmark scaffold: `aesa benchmark run`, `tests/benchmark/` (BENCH-001–002; LLM scoring deferred).

### Changed

- Product version **3.0.0**; tooling package **0.3.0**; inventory JSON `aesa_inventory_version` **0.3.0**.
- Minimum Python **>=3.15** (`tools/pyproject.toml`, CI, consumer Action).
- `aesa preflight` is now an alias of `aesa audit --profile quick`.
- Tooling refactor: modular CLI (`cli/`), adapter registry, shared `jsonio`/`pins`, typed audit profiles, Ruff py315 defaults.
- Expanded name framing: Assessment (continuous discovery/gate) while retaining Audit procedure v1.0.

### Notes

- Report schema / procedure versions remain **1.0** (no breaking report contract).
- Benchmark harness does not invoke models; corpus still validates tooling only.

## [2.3.0] — 2026-11-03

### Added

- **AESA Gate** positioning: evidence-first local preflight + agent deep review ([`docs/AESA-GATE.md`](docs/AESA-GATE.md)).
- `aesa preflight` — inventory, coverage map, ecosystem graph seed, `audit-context.md`, console summary.
- Inventory adapters (partial): hooks, plugins, subagents, automations; coverage matrix on inventory JSON.
- Bounded collector I/O (`max_files` / `max_depth` / `max_file_bytes` before content reads).
- Cursor / Claude Code skill kit: [`skills/aesa-auditor/SKILL.md`](skills/aesa-auditor/SKILL.md), [`skills/cursor/AESA.md`](skills/cursor/AESA.md).
- Version consistency checks across `VERSION`, `canonical/versions.json`, `tools/pyproject.toml`, and `tools/aesa/__init__.py`.

### Changed

- Tooling package version aligned to **0.2.0**.
- `SECURITY.md` supports **2.x**; corpus README documents CORPUS-001–010 and non-goals.
- `CONTRIBUTING.md` documents monolith regeneration via `aesa build prompts --write` (ADR-003).

### Notes

- Preflight / inventory is discovery + coverage — **not** a security clearance.
- LLM audit quality remains unbenchmarked; corpus still targets deterministic tooling.

## [2.2.0] — 2026-11-03

### Added

- SARIF 2.1.0 export: `aesa export sarif` (findings with resolvable file evidence only).
- Audit diff: `aesa diff report|graph` and `schemas/audit-diff.schema.json`.
- Digest manifest: `aesa verify manifest` and `schemas/evidence-digest-manifest.schema.json` (R-008 pilot).
- Runtime test record schema + docs (`schemas/runtime-test-record.schema.json`) — **no runtime harness**.
- Corpus cases CORPUS-009–010; recipes for source-only and staging boundary.

### Notes

- SARIF omits findings without file-backed evidence locations (by design).

## [2.1.0] — 2026-11-03

### Added

- Monolith generator: `aesa build prompts --write` / CI parity check (`canonical/prompt/` + kit segments).
- Graph semantic validation and `aesa graph paths` path search (pilot).
- `aesa validate graph`, `aesa verify digest` (SHA-256 file verification).
- Inventory adapters: A2A Agent Card JSON, `AGENTS.md` / Cursor rules discovery.
- Corpus cases CORPUS-005–008 (injection inventory, A2A card, attack paths, digest).
- Operator recipes under `docs/recipes/`.
- ADR-003 monolith generation.

### Changed

- `prompts/audit.full.md` regenerated from canonical kit sources (may differ from pre-2.1.0 monolith in Section 22+ text sourced from `03-report-contract.md`).

## [2.0.0] — 2026-11-03

Engineering transition per independent assessment (`aesa-independent-assessment-2026-11-03/`). AESA remains a **hybrid audit framework** (procedure + deterministic tooling). It is **not** a validated end-to-end scanner and does **not** certify deployments.

### Added

- Canonical sources: `canonical/schemas/`, `canonical/versions.json`, `canonical/prompt-kit.manifest.json` (R-002).
- Python tooling under `tools/aesa/`: `aesa build`, `aesa validate report`, `aesa inventory`, `aesa corpus run` (R-001, R-002, R-003, R-005 pilot).
- Semantic report validation (referential integrity, counts, CONFIRMED/evidence rules) (R-003).
- Security regression corpus under `tests/corpus/` and validation fixtures (R-001 pilot).
- Schemas: `schemas/ecosystem-graph.schema.json`, `schemas/audit-manifest.schema.json` (R-004 manifest/graph contract pilot).
- Modules: `modules/a2a.md`, `modules/multimodal.md` (R-006).
- Starter control pack: `control-packs/owasp-aisvs-1.0-starter.json` (R-007 pilot — **not** full AISVS).
- CI workflow `.github/workflows/aesa-validate.yml`.
- Docs: `docs/MIGRATION-2.0.md`, `docs/toolchain-threat-model.md`, architecture ADRs.

### Changed

- `prompts/01-core-prompt.md` — optional passive inventory tooling; A2A/multimodal module routing.
- `prompts/02-modules.md` — links to A2A and multimodal modules.
- `CONTRIBUTING.md` — canonical source workflow and validation gates.

### Notes

- Project / package version: **2.0.0**
- Bundled audit procedure version: **1.0** (unchanged)
- Baseline before transition: git `82e3ec8328a4a4e54b7604fd7f09dafd041fbb74` (release **1.1.0**)

## [1.1.0] — 2026-11-02

### Changed

- Kit files live directly under `prompts/` (removed `prompts/v1/` subdirectory); update `KIT_DIR` accordingly.
- Default `REPORT_LANGUAGE` and all operator docs are **English** (English-only framework for procedure v1.0).
  - `00-OPERATOR-GUIDE.md`, `01-core-prompt.md`, `02-modules.md`, `03-report-contract.md`, `04-passive-guardrails.md`
  - `audit.md` — kit index; `audit.full.md` — monolithic full procedure

### Notes

- Project / package version: **1.1.0**
- Bundled audit procedure version: **1.0**

## [1.0.0] — 2026-11-02

### Added

- Initial public release of **AESA** (Agent Ecosystem Security Audit) as an open-source security audit framework.
- Full audit procedure / prompt: `prompts/audit.md` (procedure version **1.0**).
- Specialized modules:
  - `modules/mcp.md`
  - `modules/skills.md`
  - `modules/plugins.md`
  - `modules/hooks.md`
  - `modules/subagents.md`
  - `modules/automations.md`
- Machine-readable report schema: `schemas/audit-report.schema.json` (JSON Schema Draft 2020-12), also available as `schemas/AI_Agent_Ecosystem_Security_Audit_v1.schema.json`.
- Usage guide: `docs/usage.md`.
- Example audit context, component inventory, and sample summary under `examples/`.
- Project governance files: `README.md`, `LICENSE` (MIT), `CONTRIBUTING.md`, `SECURITY.md`.

### Notes

- Project / package version: **1.0.0**
- Bundled audit procedure version: **1.0**
- AESA is published as a **security audit framework**, not an automated scanner.
- Narrative reports default to **English**; technical identifiers remain English.
- Passive audits must not execute target-controlled content or contact operational endpoints.
