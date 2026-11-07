# authdiff

**Authority Diff for AI agents**

`git diff` for what your AI agents can access, execute, communicate with, and
delegate — on your machine, before you install a package, and on every PR.

> Trust Nothing. Verify Everything. Secure Every Agent.

`authdiff` (product line formerly branded AESA Guard) is a local-first scanner
and CI gate. It inventories authority surfaces (skills, MCP, hooks, plugins,
subagents, CI, host configs), applies deterministic rules, and emits
evidence-backed findings. An AI agent is an optional explainer — never the
source of truth.

It is **not** a certification, marketplace badge, runtime sandbox, or substitute
for organizational risk acceptance. The `aesa` CLI name remains a compatibility
alias.

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
# Requires Python ≥3.12. Prefer PyPI when published; git tag works today:
uvx --from "git+https://github.com/roham-amd/agent-ecosystem-security-audit.git@v3.6.1#subdirectory=tools" authdiff

authdiff                  # alias: check / scan cwd
authdiff open github.com/org/some-skill
authdiff ci init          # advisory .aesa.yml + workflow
authdiff delta --baseline .aesa/baseline.json
authdiff fix --findings aesa-out/findings.json   # dry-run patches
```

Artifacts default to **`./aesa-out`**. Target `.aesa.yml` suppressions are **ignored**
unless you pass `--policy` or `--trust-target-policy`. Use `--agent` for a compact
fenced JSON digest (`decision`, `gated`, `suppressions`, `coverage_gaps`).

| Command | Purpose |
| --- | --- |
| `authdiff` / `check` / `scan` | Repo authority scan → findings, SARIF, snapshot, `pr-comment.md` |
| `authdiff doctor` | Host authority map (Cursor / Claude / Codex / …) |
| `authdiff open` / `vet` | Pre-install verdict (safe shallow clone; hooks/LFS off) |
| `authdiff delta --baseline` | New-only authority gate vs a prior baseline |
| `authdiff fix` / `harden` | Dry-run least-privilege patch templates |
| `authdiff ci init` / `init` | Write advisory `.aesa.yml` + starter workflow |
| `authdiff explain F-001` | Explain one finding from a prior scan |
| `authdiff run -- …` | Env-scrub launcher MVP (**not a sandbox**) |
| `authdiff snapshot` | MCP `tools/list` snapshot (opt-in; **not sandboxed**) |

Docs: [`docs/DOCUMENTATION-INDEX.md`](docs/DOCUMENTATION-INDEX.md) ·
[`docs/GUARD-SCAN.md`](docs/GUARD-SCAN.md) ·
[`docs/GUARD-3.6-BACKLOG.md`](docs/GUARD-3.6-BACKLOG.md) ·
demo [`examples/demo-vulnerable/`](examples/demo-vulnerable/)

Archived methodology kit: [`archive/methodology/`](archive/methodology/)
(prompts, modules, control-packs — not the product path).

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
    ref: v3.6.1   # pin tag or SHA — never float on main
- uses: ./.aesa-kit/.github/actions/aesa-gate
  with:
    path: .
    trusted-policy: "true"
    authority-diff: "true"
    install-tools-from: .aesa-kit/tools
```

With `authority-diff=true`, the Action scans the PR **base** ref and diffs it
against **head**. With `trusted-policy=true`, policy loads from the base ref.

---

## What authdiff evaluates

Skills, MCP servers, hooks, plugins, subagents, rules, automations, CI
workflows, and host agent configuration (including Claude Code settings).
Finding classes: only `SECURITY_FINDING` and `EXPOSURE` can fail CI.
`CAPABILITY` is inventory. Decisions are `BLOCK` / `REVIEW` /
`NO-GATED-FINDINGS` — never a numeric trust score. Unparsed or oversize agent
configs fail closed as `REVIEW`.

---

## Core principles

- Prefer `NOT VERIFIED` over unsupported assurance.
- Never execute, install, or contact target-controlled services during a passive audit
  (except explicit opt-in commands: `snapshot`, `run`).
- Never request or expose production secrets.
- The AI auditor explains; it is never the evidence source of truth.
- Policy that the PR author can edit is not a gate — use `trusted-policy`.

---

## License

MIT — see [`LICENSE`](LICENSE).
