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

The valuable artifact is the **PR Authority Diff comment** (≤12 lines), not a
long report.

---

## First useful minute

```bash
uv tool install git+https://github.com/roham-amd/agent-ecosystem-security-audit.git@v3.5.1#subdirectory=tools

# What authority does *this machine* already grant agents?
aesa doctor

# Should I install this skill / MCP package?
aesa vet github.com/org/some-skill

# Gate this repo
aesa init-gate
aesa scan .
aesa harden --findings aesa-out/findings.json   # dry-run patches
```

Artifacts default to **`./aesa-out`** in the current working directory (outside
the target tree). Use `--agent` on `scan` / `vet` / `explain` for a compact
fenced JSON digest.

| Command | Purpose |
| --- | --- |
| `aesa doctor` | Host authority map (Cursor / Claude Code / VS Code) |
| `aesa vet <url\|path>` | Pre-install verdict (safe shallow clone; no hooks/submodules) |
| `aesa scan <path>` | Repo scan → findings, SARIF, coverage, risk delta, `pr-comment.md` |
| `aesa harden` | Dry-run least-privilege patch templates |
| `aesa init-gate` | Write `.aesa.yml` + starter workflow |
| `aesa init-manifest` / `verify-manifest` | Declared vs observed `AUTHORITY.yml` |
| `aesa explain F-001` | Explain one finding from a prior scan |

Docs: [`docs/DOCUMENTATION-INDEX.md`](docs/DOCUMENTATION-INDEX.md) ·
[`docs/GUARD-SCAN.md`](docs/GUARD-SCAN.md) ·
[`docs/POLICY.md`](docs/POLICY.md) ·
[`docs/SECURITY-RULES.md`](docs/SECURITY-RULES.md) ·
[`docs/atlas/README.md`](docs/atlas/README.md) ·
demo [`examples/demo-vulnerable/`](examples/demo-vulnerable/)

Optional deep methodology kit: [`kit/README.md`](kit/README.md)
(`prompts/`, `modules/`, `control-packs/` — not the product path).

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
    ref: v3.5.1   # pin tag or SHA — never float on main
- uses: ./.aesa-kit/.github/actions/aesa-gate
  with:
    path: .
    fail-on: high
    trusted-policy: "true"          # load .aesa.yml from the PR base ref
    install-tools-from: .aesa-kit/tools
```

With `trusted-policy=true`, the Action loads policy from the **base ref** and
fails if the PR edits `.aesa.yml`. The gate also writes an Authority Diff
comment into the job summary (and via `gh` when available).

Full example: [`docs/aesa-consumer-gate.example.yml`](docs/aesa-consumer-gate.example.yml).

---

## What AESA evaluates

Skills, MCP servers, hooks, plugins, subagents, rules, automations, CI
workflows, and host agent configuration. Finding classes: only
`SECURITY_FINDING` and `EXPOSURE` can fail CI. `CAPABILITY` is inventory.
Rules carry `evidence_strength` (`LITERAL_CONFIG` / `INFERRED_HINT` /
`NAME_MARKER`). Decisions are `BLOCK` / `REVIEW` /
`PASS-WITH-COVERAGE-GAPS` — never a numeric trust score.

A clean result on a mostly-PARTIAL repo is a **coverage gap**, not safety.

---

## Core principles

- Prefer `NOT VERIFIED` over unsupported assurance.
- Never execute, install, or contact target-controlled services during a passive audit.
- Never request or expose production secrets.
- The AI auditor explains; it is never the evidence source of truth.
- Policy that the PR author can edit is not a gate — use `trusted-policy`.
- Target-derived strings in PR comments and agent digests are escaped/fenced.

---

## Versioning

| Kind | Current |
| --- | --- |
| Product | **3.5.1** (`VERSION`) |
| Tooling (`aesa-tools`) | **0.8.1** |
| Rule pack | **1.3** |

Authoritative alignment: [`canonical/release-manifest.json`](canonical/release-manifest.json).

---

## License / Contributing / Security

MIT — [`LICENSE`](LICENSE) · [`CONTRIBUTING.md`](CONTRIBUTING.md) · [`SECURITY.md`](SECURITY.md)

```text
AESA Guard — Authority Diff for AI agents
Project: 3.5.1
https://github.com/roham-amd/agent-ecosystem-security-audit
```
