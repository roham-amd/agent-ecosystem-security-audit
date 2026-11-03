# AESA Gate

**Agent Ecosystem Security Audit**

Evidence-first security gate for AI agent ecosystems

> **Trust Nothing. Verify Everything. Secure Every Agent.**

AESA is an open-source **hybrid audit framework** — a structured methodology, versioned audit prompts, specialized review modules, machine-readable report schemas, and **deterministic local tooling** (inventory, preflight, validation, diff, SARIF) for assessing AI agent ecosystems.

**Product positioning (2.3+):** AESA Gate helps you discover what is in an agent ecosystem, what changed, what evidence supports risk claims, and what remains `NOT VERIFIED` — then hands deep semantic review to an AI coding agent (Cursor, Claude Code, …) under hard passive-audit guardrails.

It is **not** an automated security scanner, sandbox, penetration test, marketplace certification, or substitute for organizational risk acceptance. It does **not** ship a runtime test harness or full SBOM/signature verification.

---

## What AESA helps you evaluate

Repositories and deployments that may include any combination of:

- Skills and Skill Packs
- Plugins and Connectors
- MCP Servers and Clients
- Subagents and multi-agent systems
- Rules, Hooks, Automations, and Workflows
- Tools, Commands, and Agent definitions
- Memory / RAG integrations and model providers
- Packages, scripts, binaries, and external project references

The framework answers **four separate questions**:

1. **Discovery** — What does the supplied repository actually contain or reference?
2. **Component trust** — Is each exact source, implementation, package, and consumed artifact acceptable within scope?
3. **Integration trust** — Is the component-to-host integration acceptably bounded by verified identities, permissions, and controls?
4. **Production suitability** — Is the exact combination suitable for the declared data sensitivity and operational context?

A positive answer to one question does **not** imply a positive answer to the others.

---

## 10-minute first experience

```bash
cd tools && python -m pip install -e ".[dev]"
aesa preflight /path/to/target-repo
```

You get inventory counts, a coverage map (what was discovered deterministically vs manual-only), high-priority review hints, and `NOT VERIFIED` items — **not** a pass/fail verdict. Outputs land in `aesa-out/` (`inventory.json`, `ecosystem-graph.json`, `audit-context.md`).

Then attach the kit (or [`skills/aesa-auditor/SKILL.md`](skills/aesa-auditor/SKILL.md)) to Cursor / Claude Code for evidence-bounded deep review.

---

## Repository layout

```text
agent-ecosystem-security-audit/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
├── VERSION
├── canonical/                # Source of truth (schemas, versions.json, prompt manifest)
├── tools/                    # aesa CLI — preflight, build, validate, inventory, corpus
├── skills/                   # Cursor / Claude Code skill + task shortcuts
├── tests/                    # Corpus + pytest
├── control-packs/            # Versioned control crosswalks (pilot)
├── prompts/                  # AESA kit procedure (load on demand)
│   ├── 00-OPERATOR-GUIDE.md
│   ├── 01-core-prompt.md     # Main procedure for the audit agent
│   ├── 02-modules.md
│   ├── 03-report-contract.md
│   ├── 04-passive-guardrails.md
│   ├── audit.md              # Kit index (entry pointer)
│   └── audit.full.md         # Full monolithic procedure
├── modules/
│   ├── mcp.md
│   ├── skills.md
│   ├── plugins.md
│   ├── hooks.md
│   ├── subagents.md
│   ├── automations.md
│   ├── a2a.md
│   └── multimodal.md
├── schemas/
│   ├── audit-report.schema.json
│   ├── AI_Agent_Ecosystem_Security_Audit_v1.schema.json  # synced alias
│   ├── ecosystem-graph.schema.json
│   ├── audit-manifest.schema.json
│   ├── audit-diff.schema.json
│   ├── evidence-digest-manifest.schema.json
│   └── runtime-test-record.schema.json
├── examples/
└── docs/
    ├── usage.md
    ├── AESA-GATE.md
    ├── MIGRATION-2.0.md
    ├── toolchain-threat-model.md
    └── architecture/
```

---

## Quick start

### A. Preflight + agent deep audit (recommended)

1. Install tooling and run `aesa preflight <target>`.
2. Read [`skills/aesa-auditor/SKILL.md`](skills/aesa-auditor/SKILL.md) (or [`prompts/00-OPERATOR-GUIDE.md`](prompts/00-OPERATOR-GUIDE.md)).
3. Attach [`prompts/04-passive-guardrails.md`](prompts/04-passive-guardrails.md) + fill **Audit Inputs** in [`prompts/01-core-prompt.md`](prompts/01-core-prompt.md).
4. Load only matching [`modules/`](modules/) for selected components.
5. Produce narrative + JSON; validate with `aesa validate report`.

### B. Kit-only (no Python)

1. Read [`docs/usage.md`](docs/usage.md).
2. Attach guardrails + core prompt; fill `KIT_DIR` / `WORK_DIR`.
3. For a single file, use [`prompts/audit.full.md`](prompts/audit.full.md).

### Tooling commands

```bash
cd tools && python -m pip install -e ".[dev]"
aesa preflight /path/to/target-repo
aesa inventory /path/to/target-repo
aesa validate report ../examples/sample-audit-summary.json
aesa diff report old.json new.json
aesa export sarif report.json
aesa corpus run
```

### Minimal workflow modes

| Mode | When to use | Typical stages completed |
| --- | --- | --- |
| Catalog inventory / preflight | Awesome-list / marketplace index / discovery repo | Stages 0–2 (+ `aesa preflight`) |
| Risk-prioritized deep audit | Selected authorized components | Stages 0–8 as evidence allows |
| Full ecosystem deep audit | Explicitly authorized full scope | All stages with evidence gates |

**Important:** A single GitHub URL does **not** authorize deep audit of every linked project. External sources require separate exact authorization.

---

## Core principles (summary)

- Repository-level assessment is not certification of every listed component.
- README, badges, stars, and marketplace listings are not proof of safe behavior.
- Skills, Rules, and prompts are security-relevant even without executable code.
- Individually acceptable components may form a dangerous combined data-flow path.
- Prefer `INSUFFICIENT EVIDENCE` over unsupported assurance or unsupported accusation.
- Never execute, install, or contact target-controlled services during a passive audit.
- Never request or expose production secrets.
- Narrative audit reports use **English** (`REPORT_LANGUAGE: English`).
- Do not approve sensitive production use while a material hard gate is `FAIL` or `NOT VERIFIED`.
- Inventory / preflight is **not** a security clearance.

See the kit in [`prompts/`](prompts/) or the monolithic [`prompts/audit.full.md`](prompts/audit.full.md). Product direction: [`docs/AESA-GATE.md`](docs/AESA-GATE.md).

---

## What AESA is not

| Claim | Status |
| --- | --- |
| Automated vulnerability scanner | No |
| Validated detection benchmark across all modules | No (pilot corpus covers tooling only) |
| Runtime malware detonation sandbox | No |
| Compliance certification (SOC 2, ISO, HIPAA, GDPR, …) | No |
| Guarantee that a marketplace or catalog is “safe” | No |
| Replacement for host IAM, network policy, or risk acceptance | No |

AESA helps humans and audit agents produce **evidence-bounded** decisions about exact identities, refs, versions, artifacts, hosts, and data contexts.

---

## Versioning

| Kind | Current | Meaning |
| --- | --- | --- |
| Project / package release | **2.3.0** | AESA repository packaging and public release numbering |
| Tooling (`aesa-tools`) | **0.2.0** | CLI / collectors (`canonical/versions.json` → `build_tool`) |
| Audit procedure | **1.0** (`prompts/`) | Methodology / prompt / JSON contract version inside the framework |

Breaking changes to the audit procedure, decision enums, or JSON contract bump the major procedure version under `prompts/`. Project packaging may advance independently.

---

## License

MIT — see [`LICENSE`](LICENSE).

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Security

See [`SECURITY.md`](SECURITY.md).

---

## Citation

If you use AESA in an assessment report, cite the exact procedure version and commit/tag, for example:

```text
AESA Gate — Agent Ecosystem Security Audit
Project: 2.3.0
Procedure: 1.0
https://github.com/roham-amd/agent-ecosystem-security-audit
Tag: v2.3.0
```
