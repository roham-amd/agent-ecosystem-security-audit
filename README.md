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
uvx --from "git+https://github.com/roham-amd/agent-ecosystem-security-audit.git@v3.7.0#subdirectory=tools" authdiff
# pip install aesa-tools==0.10.0

authdiff                  # ≤15-line authority map (alias: check / scan)
authdiff lock             # write AUTHORITY.lock
authdiff open github.com/org/some-skill
authdiff ci init          # .aesa.yml + workflow + CODEOWNERS
authdiff check --locked   # fail on lock drift
authdiff fix --findings aesa-out/findings.json   # dry-run patches
```

Artifacts default to **`./aesa-out`**. Target `.aesa.yml` suppressions are **ignored**
unless you pass `--policy` or `--trust-target-policy`. Use `--agent` for a compact
fenced JSON digest. Use `--full` for the long report.

| Command | Purpose |
| --- | --- |
| `authdiff lock` | Write / update `AUTHORITY.lock` |
| `authdiff` / `check` / `scan` | Repo authority scan (add `--locked`) |
| `authdiff doctor` | Host authority map (Cursor / Claude / Codex / …) |
| `authdiff open` / `vet` | Pre-install verdict (safe shallow clone; hooks/LFS off) |
| `authdiff diff lock A B` | Record-level authority lock diff |
| `authdiff fix` / `harden` | Dry-run least-privilege patch templates |
| `authdiff ci init` / `init` | `.aesa.yml` + workflow + CODEOWNERS |
| `authdiff explain F-001` | Explain one finding from a prior scan |
| `authdiff-dev` | Maintainer tools (`build`, `lint`, `corpus`, …) |

Docs: [`docs/DOCUMENTATION-INDEX.md`](docs/DOCUMENTATION-INDEX.md) ·
[`docs/AESA-GATE.md`](docs/AESA-GATE.md) ·
demo [`examples/demo-vulnerable/`](examples/demo-vulnerable/)

Archived methodology kit: [`archive/methodology/`](archive/methodology/)
(prompts, modules, control-packs — not the product path).

---

## CI gate (tamper-resistant)

Single recipe (PyPI + Action). Full example:
[`docs/aesa-consumer-gate.example.yml`](docs/aesa-consumer-gate.example.yml).

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
- run: pip install "aesa-tools==0.10.0"
- uses: roham-amd/agent-ecosystem-security-audit/.github/actions/aesa-gate@v3.7.0
  with:
    path: .
    trusted-policy: "true"
    authority-diff: "true"
    locked: "false"   # set true after committing AUTHORITY.lock
    install-tools-from: path
```

With `authority-diff=true`, the Action scans the PR **base** ref and diffs it
against **head**. With `trusted-policy=true`, policy loads from the base ref.
With `locked=true`, AUTHORITY.lock drift fails the check (Action v2).

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
