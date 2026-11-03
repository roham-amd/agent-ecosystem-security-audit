# AESA Guard

**Agent Ecosystem Security Assessment — Guard**

Local-first security intelligence and change gate for AI-agent ecosystems.

> **Trust Nothing. Verify Everything. Secure Every Agent.**

AESA Guard discovers what your agents can access, execute, and trust; emits
evidence-backed deterministic observations; and gates dangerous changes in CI.
Deep semantic review remains optional via an AI coding agent under hard
passive-audit guardrails.

**Product positioning (3.1):** One primary command (`aesa scan`), deterministic
security rules, baselines/risk diffs, SARIF, and a CI gate — plus the existing
methodology, modules, schemas, and auditor skill.

It is **not** a certification authority, marketplace badge, runtime sandbox, or
substitute for organizational risk acceptance. Deterministic findings are
`OBSERVED`/`POTENTIAL` evidence, not confirmed exploits.

**Documentation map:** [`docs/DOCUMENTATION-INDEX.md`](docs/DOCUMENTATION-INDEX.md)

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
- Host agent configuration, browser agents, and CI/CD surfaces that bind them

The framework answers **four separate questions**:

1. **Discovery** — What does the supplied repository actually contain or reference?
2. **Component trust** — Is each exact source, implementation, package, and consumed artifact acceptable within scope?
3. **Integration trust** — Is the component-to-host integration acceptably bounded by verified identities, permissions, and controls?
4. **Production suitability** — Is the exact combination suitable for the declared data sensitivity and operational context?

A positive answer to one question does **not** imply the others.

---

## 10-minute first experience

```bash
cd tools && uv sync --locked
uv run aesa scan /path/to/target-repo
```

You get a terminal security summary: components, authority-bearing surfaces,
external destinations, deterministic findings with evidence paths, and coverage
gaps. Artifacts land in `aesa-out/`:

| Artifact | Purpose |
| --- | --- |
| `findings.json` | Guard findings + evidence registry + capabilities |
| `findings.sarif.json` | SARIF 2.1.0 for CI |
| `inventory.json` | Component inventory + coverage |
| `ecosystem-graph.json` | Structural graph seed |
| `scan-summary.txt` / `scan-report.md` | Human reports |
| `profile.json` | Scan metadata |

```bash
uv run aesa explain F-001 -o aesa-out
uv run aesa baseline save -o aesa-out
```

| Next step | Doc |
| --- | --- |
| Scan pipeline details | [`docs/GUARD-SCAN.md`](docs/GUARD-SCAN.md) |
| Rule catalog | [`docs/SECURITY-RULES.md`](docs/SECURITY-RULES.md) |
| CLI flags | [`docs/CLI-REFERENCE.md`](docs/CLI-REFERENCE.md) |
| Optional AI deep review | [`skills/aesa-auditor/SKILL.md`](skills/aesa-auditor/SKILL.md) |
| Short primer | [`docs/AESA-GATE.md`](docs/AESA-GATE.md) |
| Product contract | [`docs/AESA-3.0-PRODUCT-SPEC.md`](docs/AESA-3.0-PRODUCT-SPEC.md) |
| 3.0 → 3.1 migration | [`docs/MIGRATION-3.1.md`](docs/MIGRATION-3.1.md) |

---

## Repository layout

```text
agent-ecosystem-security-audit/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
├── VERSION                      # product version (3.3.1)
├── Dockerfile                   # python:3.15.2-slim-trixie@sha256 + uv
├── docker-compose.yml
├── canonical/                   # versions.json, schemas, prompt manifest
├── tools/                       # aesa CLI (scan, audit, validate, …)
├── skills/                      # Cursor / Claude Code auditor skill
├── tests/                       # corpus + AgentSecBench + pytest
├── control-packs/               # control crosswalks (pilot)
├── prompts/                     # procedure kit (load on demand)
│   ├── 00-OPERATOR-GUIDE.md
│   ├── 01-core-prompt.md
│   ├── 02-modules.md
│   ├── 03-report-contract.md
│   ├── 04-passive-guardrails.md
│   ├── audit.md
│   └── audit.full.md            # generated monolith
├── modules/                     # specialized checklists (see modules/README.md)
├── schemas/                     # published JSON Schemas (see schemas/README.md)
├── examples/
├── docs/                        # see docs/DOCUMENTATION-INDEX.md
│   ├── DOCUMENTATION-INDEX.md
│   ├── GUARD-SCAN.md
│   ├── CLI-REFERENCE.md
│   ├── SECURITY-RULES.md
│   ├── EVIDENCE-MODEL.md
│   ├── AESA-GATE.md
│   ├── usage.md
│   ├── docker-agent-audit.md
│   ├── threat-scenarios.md
│   ├── recipes/
│   └── architecture/
└── .github/actions/aesa-gate/   # CI Guard Action
```

---

## Quick start

### A. Guard scan + optional agent deep review (recommended)

1. `uv sync --locked` in `tools/`, then `aesa scan <target>`.
2. Review `aesa-out/scan-summary.txt` and `findings.json`.
3. Attach [`skills/aesa-auditor/SKILL.md`](skills/aesa-auditor/SKILL.md) + [`prompts/04-passive-guardrails.md`](prompts/04-passive-guardrails.md).
4. Load only matching [`modules/`](modules/) (index: [`modules/README.md`](modules/README.md)).
5. Emit structured claims; validate with `aesa validate claim`.
6. Produce narrative + JSON; validate with `aesa validate report`.

Operator guide: [`docs/usage.md`](docs/usage.md). Evidence rules: [`docs/EVIDENCE-MODEL.md`](docs/EVIDENCE-MODEL.md).

### B. Kit-only (no Python)

1. Read [`docs/usage.md`](docs/usage.md) and [`prompts/00-OPERATOR-GUIDE.md`](prompts/00-OPERATOR-GUIDE.md).
2. Attach guardrails + core prompt; fill `KIT_DIR` / `WORK_DIR`.
3. For a single file, use [`prompts/audit.full.md`](prompts/audit.full.md).

### C. Audit profiles (agent handoff package)

```bash
uv run aesa audit /path/to/target --profile quick|standard|deployment
```

Use when you need `audit-context.md` stage checklists; prefer **scan** for security observations first.

### Tooling commands

Stack: **uv + pyproject.toml + uv.lock + Ruff + Pytest + mypy** — [`tools/README.md`](tools/README.md).  
Full CLI: [`docs/CLI-REFERENCE.md`](docs/CLI-REFERENCE.md).

```bash
cd tools && uv sync --locked
uv run aesa scan /path/to/target-repo
uv run aesa explain F-001 -o ../aesa-out
uv run aesa baseline save -o ../aesa-out
uv run aesa audit /path/to/target-repo --profile standard
uv run aesa inventory /path/to/target-repo
uv run aesa validate report ../examples/sample-audit-summary.json
uv run aesa validate claim path/to/claim.json
uv run aesa diff risk baseline.json findings.json
uv run aesa export sarif findings.json
uv run aesa corpus run
uv run aesa benchmark run
uv run --locked pytest -q ../tests
```

### Docker + AI agent (Cursor, Claude Code, Codex, …)

Walkthrough: [`docs/docker-agent-audit.md`](docs/docker-agent-audit.md).

```bash
docker compose build
TARGET=/path/to/target-repo docker compose run --rm aesa \
  scan /work -o /work/aesa-out
```

Then attach the auditor skill and hand the agent `aesa-out/`.

### CI gate

Composite Action [`.github/actions/aesa-gate`](.github/actions/aesa-gate) + example
[`docs/aesa-consumer-gate.example.yml`](docs/aesa-consumer-gate.example.yml).

Supports `mode=scan`, `fail-on`, baseline risk delta, coverage reporting, and SARIF path notes. Inputs are passed via environment variables (shell-injection hardened).

### Workflow modes

| Mode | When to use | Typical completion |
| --- | --- | --- |
| Guard scan | First useful security observation | Deterministic findings + coverage |
| Quick inventory / audit quick | Catalog / first look handoff | Stages 0–2 |
| Standard assessment | Selected authorized components | Stages 0–8 as evidence allows |
| Deployment suitability | Host + data sensitivity declared | Full gate worksheet |

**Important:** A single GitHub URL does **not** authorize deep audit of every linked project.

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
- Inventory / scan without coverage context is **not** a security clearance.
- Do not invent a single numeric trust score; keep severity, confidence, and coverage separate.

Procedure kit: [`prompts/`](prompts/). Threat scenarios: [`docs/threat-scenarios.md`](docs/threat-scenarios.md). Toolchain threats: [`docs/toolchain-threat-model.md`](docs/toolchain-threat-model.md).

---

## What AESA is not

| Claim | Status |
| --- | --- |
| Automated vulnerability scanner that proves systems are safe | No |
| Validated LLM detection benchmark (precision/recall across models) | No (AgentSecBench fixtures only; LLM runner deferred) |
| Runtime malware detonation sandbox | No |
| Compliance certification (SOC 2, ISO, HIPAA, GDPR, …) | No |
| Marketplace “certified secure” badge | No |
| Replacement for host IAM, network policy, or risk acceptance | No |

AESA helps humans and audit agents produce **evidence-bounded** decisions about exact identities, refs, versions, artifacts, hosts, and data contexts.

---

## Versioning

| Kind | Current | Meaning |
| --- | --- | --- |
| Project / package release | **3.3.1** | AESA Guard product release (`VERSION`) |
| Tooling (`aesa-tools`) | **0.6.1** | CLI / collectors / Guard rules / hosts |
| Audit procedure | **1.0** (`prompts/`) | Methodology / prompt / JSON contract |
| AgentSecBench | **0.3.0** / LLM **0.3.0** | Deterministic + governed offline LLM scoring |
| Report / graph schemas | **1.0** | See [`schemas/README.md`](schemas/README.md) |

Authoritative alignment: [`canonical/release-manifest.json`](canonical/release-manifest.json) plus `VERSION` ↔ `canonical/versions.json` ↔ `tools/pyproject.toml` ↔ `tools/aesa/__init__.py` (enforced by `aesa build`).

---

## License

MIT — see [`LICENSE`](LICENSE).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Security

See [`SECURITY.md`](SECURITY.md).

## Citation

```text
AESA Guard — Agent Ecosystem Security Assessment
Project: 3.3.1
Procedure: 1.0
https://github.com/roham-amd/agent-ecosystem-security-audit
Tag: v3.3.1
```
