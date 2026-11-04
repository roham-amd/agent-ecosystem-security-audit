# AESA Guard

**Authority Diff for AI agents**

`git diff` for what your AI agents can access, execute, communicate with, and
delegate — on your machine, before you install a package, and on every PR.

> Trust Nothing. Verify Everything. Secure Every Agent.

AESA Guard is a local-first scanner and CI gate. It inventories authority
surfaces (skills, MCP, hooks, plugins, subagents, CI, host configs), applies
deterministic rules, and emits evidence-backed findings. An AI agent is an
optional explainer — never the source of truth.

It is **not** a certification, marketplace badge, runtime sandbox, or substitute
for organizational risk acceptance.

---

## Job to be done

> Before I install, merge, deploy, or upgrade an AI-agent integration, tell me
> what authority it introduces, who receives that authority, what data can flow
> through it, and what materially changed.

---

## First useful minute

```bash
uv tool install git+https://github.com/roham-amd/agent-ecosystem-security-audit.git@main#subdirectory=tools

# What authority does *this machine* already grant agents?
aesa doctor

# Should I install this skill / MCP package?
aesa vet github.com/org/some-skill

# Gate this repo
aesa init-gate
aesa scan .
```

Artifacts default to **`./aesa-out`** in the current working directory (outside
the target tree).

| Command | Purpose |
| --- | --- |
| `aesa doctor` | Host authority map (Cursor / Claude Code / VS Code) |
| `aesa vet <url\|path>` | Pre-install verdict (safe shallow clone; no hooks/submodules) |
| `aesa scan <path>` | Repo scan → findings, SARIF, coverage, risk delta |
| `aesa init-gate` | Write `.aesa.yml` + starter workflow |
| `aesa explain F-001` | Explain one finding from a prior scan |

Docs: [`docs/DOCUMENTATION-INDEX.md`](docs/DOCUMENTATION-INDEX.md) ·
scan pipeline [`docs/GUARD-SCAN.md`](docs/GUARD-SCAN.md) ·
policy [`docs/POLICY.md`](docs/POLICY.md) ·
rules [`docs/SECURITY-RULES.md`](docs/SECURITY-RULES.md) ·
coverage [`docs/COVERAGE-MATRIX.md`](docs/COVERAGE-MATRIX.md)

---

## CI gate (tamper-resistant)

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
- uses: actions/checkout@v4
  with:
    repository: roham-amd/agent-ecosystem-security-audit
    path: .aesa-kit
    ref: v3.5.0   # pin tag or SHA — never float on main
- uses: ./.aesa-kit/.github/actions/aesa-gate
  with:
    path: .
    fail-on: high
    trusted-policy: "true"          # load .aesa.yml from the PR base ref
    install-tools-from: .aesa-kit/tools
```

With `trusted-policy=true`, the Action loads policy from the **base ref** and
fails if the PR edits `.aesa.yml`. Tooling installs from the pinned AESA kit
(or Action-bundled `tools/`), not from a PR-controlled workspace `tools/` by
default.

Full example: [`docs/aesa-consumer-gate.example.yml`](docs/aesa-consumer-gate.example.yml).

---

## What AESA evaluates

Skills, MCP servers, hooks, plugins, subagents, rules, automations, CI
workflows, and host agent configuration. Four separate questions:

1. **Discovery** — What does the target contain or reference?
2. **Component trust** — Is each exact source/artifact acceptable?
3. **Integration trust** — Is the host binding acceptably bounded?
4. **Production suitability** — Fit for the declared data sensitivity?

A yes to one does **not** imply the others. Incomplete coverage
(`PARTIAL` / `MANUAL_ONLY`) means **no findings ≠ safe**.

Finding classes: only `SECURITY_FINDING` and `EXPOSURE` can fail CI.
`CAPABILITY` is inventory. Rules also carry `evidence_strength`
(`LITERAL_CONFIG` / `INFERRED_HINT` / `NAME_MARKER`).

---

## Core principles

- Prefer `NOT VERIFIED` over unsupported assurance.
- Never execute, install, or contact target-controlled services during a passive audit.
- Never request or expose production secrets.
- The AI auditor explains; it is never the evidence source of truth.
- Policy that the PR author can edit is not a gate — use `trusted-policy`.

---

## Versioning

| Kind | Current |
| --- | --- |
| Product | **3.5.0** (`VERSION`) |
| Tooling (`aesa-tools`) | **0.8.0** |
| Rule pack | **1.2** |

Authoritative alignment: [`canonical/release-manifest.json`](canonical/release-manifest.json).

---

## License / Contributing / Security

MIT — [`LICENSE`](LICENSE) · [`CONTRIBUTING.md`](CONTRIBUTING.md) · [`SECURITY.md`](SECURITY.md)

```text
AESA Guard — Authority Diff for AI agents
Project: 3.5.0
https://github.com/roham-amd/agent-ecosystem-security-audit
```
