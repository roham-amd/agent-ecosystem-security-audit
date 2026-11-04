# AESA Guard

**Agent Ecosystem Security Gate**

Find and gate risky changes to what your AI agents can access, execute,
communicate with, and delegate.

> **Trust Nothing. Verify Everything. Secure Every Agent.**

AESA Guard is a local-first security scanner and PR change gate for AI-agent
ecosystems. It discovers authority surfaces, emits evidence-backed deterministic
observations, and blocks dangerous changes in CI. Deep semantic review remains
optional via an AI coding agent under hard passive-audit guardrails.

**Product positioning (3.4):** One primary command (`aesa scan`), deterministic
security rules, `.aesa.yml` policy, baselines/risk diffs, SARIF, and a CI gate —
plus the existing methodology, modules, schemas, and optional auditor skill.

It is **not** a certification authority, marketplace badge, runtime sandbox, or
substitute for organizational risk acceptance. Deterministic findings are
`OBSERVED`/`POTENTIAL` evidence, not confirmed exploits.

**Documentation map:** [`docs/DOCUMENTATION-INDEX.md`](docs/DOCUMENTATION-INDEX.md)

---

## Job to be done

> Before I install, merge, deploy, or upgrade an AI-agent integration, tell me
> what authority it introduces, who receives that authority, what data can flow
> through it, and what materially changed.

---

## 10-minute first experience

```bash
uv tool install git+https://github.com/roham-amd/agent-ecosystem-security-audit.git@main#subdirectory=tools
aesa scan /path/to/target-repo
```

Or from a clone: `cd tools && uv sync --locked && uv run aesa scan /path/to/target-repo`.

Full install options: [`docs/INSTALL.md`](docs/INSTALL.md).

Artifacts default to **`./aesa-out`** in your current working directory (not
inside the target repository), keeping the target tree read-only by default.

You get a terminal security summary: authority surfaces, external destinations,
deterministic findings with evidence paths, adapter coverage, and explicit
`NOT VERIFIED` gaps.

| Artifact | Purpose |
| --- | --- |
| `findings.json` | Guard findings + evidence registry + capabilities |
| `findings.sarif.json` | SARIF 2.1.0 for CI |
| `inventory.json` | Component inventory + coverage |
| `ecosystem-graph.json` | Structural graph seed |
| `scan-summary.txt` / `scan-report.md` | Human decision reports |
| `profile.json` | Scan metadata |

```bash
uv run aesa explain F-001 -o aesa-out
uv run aesa baseline save -o aesa-out
```

| Next step | Doc |
| --- | --- |
| Scan pipeline details | [`docs/GUARD-SCAN.md`](docs/GUARD-SCAN.md) |
| Coverage matrix | [`docs/COVERAGE-MATRIX.md`](docs/COVERAGE-MATRIX.md) |
| Policy file | [`docs/POLICY.md`](docs/POLICY.md) |
| Rule catalog | [`docs/SECURITY-RULES.md`](docs/SECURITY-RULES.md) |
| CLI flags | [`docs/CLI-REFERENCE.md`](docs/CLI-REFERENCE.md) |
| Optional AI deep review | [`skills/aesa-auditor/SKILL.md`](skills/aesa-auditor/SKILL.md) |
| Short primer | [`docs/AESA-GATE.md`](docs/AESA-GATE.md) |
| 3.4 productization backlog | [`docs/GUARD-3.4-BACKLOG.md`](docs/GUARD-3.4-BACKLOG.md) |

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

## Repository layout

```text
agent-ecosystem-security-audit/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
├── VERSION                      # product version (3.4.0)
├── Dockerfile
├── docker-compose.yml
├── canonical/                   # versions.json, schemas, release-manifest
├── tools/                       # aesa CLI (scan, audit, validate, …)
├── skills/                      # Cursor / Claude Code auditor skill
├── tests/                       # corpus + AgentSecBench + pytest
├── control-packs/               # control crosswalks (pilot)
├── prompts/                     # procedure kit (load on demand)
├── modules/                     # specialized checklists
├── schemas/                     # published JSON Schemas
├── examples/                    # sample audit + Guard scan artifacts
├── docs/                        # see docs/DOCUMENTATION-INDEX.md
└── .github/actions/aesa-gate/   # CI Guard Action
```

---

## Quick start

### A. Guard scan + optional agent deep review (recommended)

1. `uv sync --locked` in `tools/`, then `aesa scan <target>`.
2. Review `aesa-out/scan-summary.txt` and `findings.json`.
3. Optionally add `.aesa.yml` policy (see [`docs/POLICY.md`](docs/POLICY.md)).
4. Attach [`skills/aesa-auditor/SKILL.md`](skills/aesa-auditor/SKILL.md) + [`prompts/04-passive-guardrails.md`](prompts/04-passive-guardrails.md) for deeper review.
5. Load only matching [`modules/`](modules/) (index: [`modules/README.md`](modules/README.md)).
6. Emit structured claims; validate with `aesa validate claim`.
7. Produce narrative + JSON; validate with `aesa validate report`.

Operator guide: [`docs/usage.md`](docs/usage.md). Evidence rules: [`docs/EVIDENCE-MODEL.md`](docs/EVIDENCE-MODEL.md).

### B. Kit-only (no Python)

1. Read [`docs/usage.md`](docs/usage.md) and [`prompts/00-OPERATOR-GUIDE.md`](prompts/00-OPERATOR-GUIDE.md).
2. Attach guardrails + [`prompts/scan-triage.md`](prompts/scan-triage.md) for scan-first triage.
3. For full deep procedure, use [`prompts/01-core-prompt.md`](prompts/01-core-prompt.md) or [`prompts/audit.full.md`](prompts/audit.full.md).

### C. Audit profiles (agent handoff package)

```bash
uv run aesa audit /path/to/target --profile standard
```

Use when you need `audit-context.md` stage checklists; prefer **scan** for security observations first.

### CI gate

Composite Action [`.github/actions/aesa-gate`](.github/actions/aesa-gate) + example
[`docs/aesa-consumer-gate.example.yml`](docs/aesa-consumer-gate.example.yml).

**Pin an immutable AESA release tag or commit** — do not float on `main`.

Supports `mode=scan`, `fail-on`, baseline risk delta, coverage reporting, and SARIF path notes.

### Workflow modes

| Mode | When to use | Typical completion |
| --- | --- | --- |
| Guard scan | First useful security observation | Deterministic findings + coverage |
| Quick inventory / audit quick | Catalog / first look handoff | Stages 0–2 |
| Standard assessment | Selected authorized components | Stages 0–8 as evidence allows |
| Deployment suitability | Host + data sensitivity declared | Full gate worksheet |

---

## Core principles (summary)

- Repository-level assessment is not certification of every listed component.
- README, badges, stars, and marketplace listings are not proof of safe behavior.
- Skills, Rules, and prompts are security-relevant even without executable code.
- Individually acceptable components may form a dangerous combined data-flow path.
- Prefer `INSUFFICIENT EVIDENCE` over unsupported assurance or unsupported accusation.
- Never execute, install, or contact target-controlled services during a passive audit.
- Never request or expose production secrets.
- Do not approve sensitive production use while a material hard gate is `FAIL` or `NOT VERIFIED`.
- Inventory / scan without coverage context is **not** a security clearance.
- Do not invent a single numeric trust score; keep severity, confidence, and coverage separate.
- The AI auditor explains and investigates; it is never the evidence source of truth.

---

## What AESA is not

| Claim | Status |
| --- | --- |
| Automated vulnerability scanner that proves systems are safe | No |
| Validated LLM detection benchmark (precision/recall across models) | No (AgentSecBench fixtures only; live models deferred; external N=0) |
| Runtime malware detonation sandbox | No |
| Compliance certification (SOC 2, ISO, HIPAA, GDPR, …) | No |
| Marketplace “certified secure” badge | No |
| Replacement for host IAM, network policy, or risk acceptance | No |

---

## Versioning

| Kind | Current | Meaning |
| --- | --- | --- |
| Project / package release | **3.4.0** | AESA Guard product line (`VERSION`) |
| Tooling (`aesa-tools`) | **0.7.0** | CLI / collectors / Guard rules / policy |
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
AESA Guard — Agent Ecosystem Security Gate
Project: 3.4.0
Procedure: 1.0
https://github.com/roham-amd/agent-ecosystem-security-audit
```
