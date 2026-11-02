# Changelog

All notable changes to the AESA framework are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses semantic versioning for packaged releases (`1.1.0`, …).
The included audit procedure version remains independently numbered (procedure **1.0** under `prompts/`).

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
