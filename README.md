# AESA

**Agent Ecosystem Security Assessment**

Evidence-first security for AI-agent ecosystems

> **Trust Nothing. Verify Everything. Secure Every Agent.**

AESA is an open-source **local-first security toolchain** — a structured methodology, versioned audit prompts, specialized review modules, machine-readable report schemas, and **deterministic tooling** (`aesa audit`, inventory, validation, diff, SARIF, CI Action) for assessing AI agent ecosystems.

**Product positioning (3.0):** Discover agent components and trust relationships, establish what they can do with evidence, prioritize what to fix or verify, and gate change in CI — with deep semantic review by an AI coding agent under hard passive-audit guardrails.

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
cd tools && uv sync --locked
uv run aesa audit /path/to/target-repo --profile quick
```

You get inventory counts, a coverage map (what was discovered deterministically vs manual-only), high-priority review hints, and `NOT VERIFIED` items — **not** a pass/fail verdict. Outputs land in `aesa-out/` (`inventory.json`, `ecosystem-graph.json`, `audit-context.md`, `profile.json`).

Then attach the kit (or [`skills/aesa-auditor/SKILL.md`](skills/aesa-auditor/SKILL.md)) to Cursor / Claude Code for evidence-bounded deep review. Spec: [`docs/AESA-3.0-PRODUCT-SPEC.md`](docs/AESA-3.0-PRODUCT-SPEC.md).

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
├── Dockerfile                # python:3.15.2-slim-trixie@sha256 + uv (tag@digest)
├── docker-compose.yml
├── canonical/                # Source of truth (schemas, versions.json, prompt manifest)
├── tools/                    # aesa CLI — audit, build, validate, inventory, corpus
├── skills/                   # Cursor / Claude Code skill + task shortcuts
├── tests/                    # Corpus + benchmark + pytest
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
├── docs/
│   ├── AESA-3.0-PRODUCT-SPEC.md
│   ├── usage.md
│   ├── docker-agent-audit.md   # Docker preflight + AI agent deep review
│   ├── AESA-GATE.md
│   ├── MIGRATION-2.0.md
│   ├── toolchain-threat-model.md
│   └── architecture/
├── .github/actions/aesa-gate/
└── tests/benchmark/
```

---

## Quick start

### A. Unified audit + agent deep review (recommended)

1. Install tooling and run `aesa audit <target> --profile quick` (then `standard` for handoff depth).
2. Read [`skills/aesa-auditor/SKILL.md`](skills/aesa-auditor/SKILL.md) (or [`prompts/00-OPERATOR-GUIDE.md`](prompts/00-OPERATOR-GUIDE.md)).
3. Attach [`prompts/04-passive-guardrails.md`](prompts/04-passive-guardrails.md) + fill **Audit Inputs** in [`prompts/01-core-prompt.md`](prompts/01-core-prompt.md).
4. Load only matching [`modules/`](modules/) for selected components.
5. Produce narrative + JSON; validate with `aesa validate report`.

### B. Kit-only (no Python)

1. Read [`docs/usage.md`](docs/usage.md).
2. Attach guardrails + core prompt; fill `KIT_DIR` / `WORK_DIR`.
3. For a single file, use [`prompts/audit.full.md`](prompts/audit.full.md).

### Tooling commands

Stack: **uv + pyproject.toml + uv.lock + Ruff + Pytest + mypy** (see [`tools/README.md`](tools/README.md)).

```bash
cd tools && uv sync --locked
uv run aesa audit /path/to/target-repo --profile quick
uv run aesa audit /path/to/target-repo --profile standard
uv run aesa inventory /path/to/target-repo
uv run aesa validate report ../examples/sample-audit-summary.json
uv run aesa diff report old.json new.json
uv run aesa export sarif report.json
uv run aesa corpus run
uv run aesa benchmark run
uv run --locked mypy aesa
uv run --locked pip-audit
uv run --locked pytest -q ../tests
```

### Docker + AI agent (Cursor, Claude Code, Codex, …)

Full walkthrough: [`docs/docker-agent-audit.md`](docs/docker-agent-audit.md).

```bash
docker compose build
# Mount the target clone; write aesa-out/ inside it
TARGET=/path/to/target-repo docker compose run --rm aesa \
  audit /work --profile standard -o /work/aesa-out
```

Then open Cursor / Claude Code / Codex / Antigravity (or similar), attach
[`skills/aesa-auditor/SKILL.md`](skills/aesa-auditor/SKILL.md) +
[`prompts/04-passive-guardrails.md`](prompts/04-passive-guardrails.md), and hand the agent
`aesa-out/audit-context.md` + `inventory.json` for deep review.

Base image pins are `name:tag@sha256:…` in [`Dockerfile`](Dockerfile); Dependabot’s `docker` ecosystem updates them weekly.

### Minimal workflow modes

| Mode | When to use | Typical stages completed |
| --- | --- | --- |
| Quick inventory | Awesome-list / marketplace index / first look | Stages 0–2 (`--profile quick`) |
| Standard assessment | Selected authorized components | Stages 0–8 as evidence allows (`--profile standard`) |
| Deployment suitability | Host + data sensitivity declared | Full gate worksheet (`--profile deployment`) |

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
- Inventory / `aesa audit` is **not** a security clearance.

See the kit in [`prompts/`](prompts/) or the monolithic [`prompts/audit.full.md`](prompts/audit.full.md). Product spec: [`docs/AESA-3.0-PRODUCT-SPEC.md`](docs/AESA-3.0-PRODUCT-SPEC.md).

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
| Project / package release | **3.0.0** | AESA repository packaging and public release numbering |
| Tooling (`aesa-tools`) | **0.3.0** | CLI / collectors (`canonical/versions.json` → `build_tool`) |
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
AESA — Agent Ecosystem Security Assessment
Project: 3.0.0
Procedure: 1.0
https://github.com/roham-amd/agent-ecosystem-security-audit
Tag: v3.0.0
```
