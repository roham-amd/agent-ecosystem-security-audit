# AESA

**Agent Ecosystem Security Audit**

A Security Audit Framework for AI Agent Ecosystems

> **Trust Nothing. Verify Everything. Secure Every Agent.**

AESA is an open-source **security audit framework** — a structured methodology, versioned audit prompts, specialized review modules, and machine-readable report schemas for assessing AI agent ecosystems.

It is **not** an automated security scanner, sandbox, penetration test, marketplace certification, or substitute for organizational risk acceptance.

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

## Repository layout

```text
agent-ecosystem-security-audit/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
├── prompts/
│   └── v1/
│       └── audit.md          # Full AESA v1.0 audit procedure / prompt
├── modules/
│   ├── mcp.md
│   ├── skills.md
│   ├── plugins.md
│   ├── hooks.md
│   ├── subagents.md
│   └── automations.md
├── schemas/
│   ├── audit-report.schema.json
│   └── AI_Agent_Ecosystem_Security_Audit_v1.schema.json  # same contract; canonical name in v1.0
├── examples/
│   ├── sample-audit-context.yaml
│   ├── sample-component-inventory.json
│   └── sample-audit-summary.json
└── docs/
    └── usage.md
```

---

## Quick start

1. Read [`docs/usage.md`](docs/usage.md).
2. Copy the current procedure from [`prompts/v1/audit.md`](prompts/v1/audit.md) into your audit agent or review workflow.
3. Fill the **Audit Inputs** (repository URL, authorization scope, host context, data sensitivity).
4. Apply relevant specialized modules from [`modules/`](modules/).
5. Produce a narrative report plus a machine-readable summary conforming to [`schemas/audit-report.schema.json`](schemas/audit-report.schema.json).

### Minimal workflow modes

| Mode | When to use | Typical stages completed |
| --- | --- | --- |
| Catalog inventory | Awesome-list / marketplace index / discovery repo | Stages 0–2 |
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
- Do not approve sensitive production use while a material hard gate is `FAIL` or `NOT VERIFIED`.

See the full procedure in [`prompts/v1/audit.md`](prompts/v1/audit.md).

---

## What AESA is not

| Claim | Status |
| --- | --- |
| Automated vulnerability scanner | No |
| Runtime malware detonation sandbox | No |
| Compliance certification (SOC 2, ISO, HIPAA, GDPR, …) | No |
| Guarantee that a marketplace or catalog is “safe” | No |
| Replacement for host IAM, network policy, or risk acceptance | No |

AESA helps humans and audit agents produce **evidence-bounded** decisions about exact identities, refs, versions, artifacts, hosts, and data contexts.

---

## Versioning

| Kind | Current | Meaning |
| --- | --- | --- |
| Project / package release | **1.0.0** | AESA repository packaging and public release numbering |
| Audit procedure | **1.0** (`prompts/v1/`) | Methodology / prompt / JSON contract version inside the framework |

Breaking changes to the audit procedure, decision enums, or JSON contract bump the major procedure version under `prompts/`. Project packaging may advance independently (for example `1.x.y`).

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
AESA — Agent Ecosystem Security Audit
Project: 1.0.0
Procedure: 1.0
https://github.com/roham-amd/agent-ecosystem-security-audit
Tag: v1.0.0
```
