# Changelog

All notable changes to the AESA framework are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses semantic versioning for packaged releases (`2.0.0`, …).
The included audit procedure version remains independently numbered (procedure **1.0** under `prompts/`).

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
