# authdiff

**Authority Diff for AI agents**

> Know what authority your AI agents gain, before install and on every pull request.

`git diff` for what your AI agents can access, execute, communicate with, and
delegate — on your machine, before you install a package, and on every PR.

`authdiff` (product line formerly branded AESA Guard) is a local-first scanner
and CI gate. It inventories authority surfaces (skills, MCP, hooks, plugins,
subagents, CI, host configs), applies deterministic rules, and emits
evidence-backed findings. An AI agent is an optional explainer — never the
source of truth.

It is **not** a certification, marketplace badge, runtime sandbox, or substitute
for organizational risk acceptance. The `aesa` CLI name remains a compatibility
alias. AESA and authdiff are the **same product** — see [`docs/PRODUCT.md`](docs/PRODUCT.md).

---

## Job to be done

> Before I install, merge, deploy, or upgrade an AI-agent integration, tell me
> what authority it introduces, who receives that authority, what data can flow
> through it, and what materially changed.

Three questions:

1. What authority do I already have?
2. What authority does this change introduce?
3. Is that change approved?

The valuable artifact is the **PR Authority Diff comment** (≤12 lines) plus
committed [`AUTHORITY.lock`](docs/AUTHORITY-LOCK.md) — not a long report.

---

## First useful minute

```bash
# Requires Python ≥3.12. One canonical install (git tag today; PyPI when published):
uvx --from "git+https://github.com/roham-amd/agent-ecosystem-security-audit.git@v3.8.0#subdirectory=tools" authdiff
# pip install aesa-tools==0.11.0

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

### Core commands

| Command | Purpose |
| --- | --- |
| `authdiff` / `check` / `scan` | Repo authority scan (add `--locked`) |
| `authdiff doctor` | Host authority map |
| `authdiff open` / `vet` | Pre-install verdict (safe shallow clone) |
| `authdiff lock` | Write / update `AUTHORITY.lock` |
| `authdiff ci init` | `.aesa.yml` + workflow + CODEOWNERS |

Review / advanced / maintainer tiers: [`docs/PRODUCT.md`](docs/PRODUCT.md) ·
[`docs/CLI-REFERENCE.md`](docs/CLI-REFERENCE.md).

Docs: [`docs/DOCUMENTATION-INDEX.md`](docs/DOCUMENTATION-INDEX.md) ·
[`docs/AUTHORITY-LOCK.md`](docs/AUTHORITY-LOCK.md) ·
[`docs/COVERAGE-MATRIX.md`](docs/COVERAGE-MATRIX.md) ·
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
- run: pip install "aesa-tools==0.11.0"
- uses: roham-amd/agent-ecosystem-security-audit/.github/actions/aesa-gate@v3.8.0
  with:
    path: .
    trusted-policy: "true"
    authority-diff: "true"
    locked: "false"   # set true after committing AUTHORITY.lock
    install-tools-from: path
```

Prefer pinning the Action by **immutable commit SHA** in high-assurance repos
(see [`docs/AESA-GATE.md`](docs/AESA-GATE.md)).

With `authority-diff=true`, the Action scans the PR **base** ref and diffs it
against **head**. With `trusted-policy=true`, policy loads from the base ref.
With `locked=true`, AUTHORITY.lock drift fails the check.

---

## What authdiff evaluates

Skills, MCP servers, hooks, plugins, subagents, rules, automations, CI
workflows, and host agent configuration. Finding classes: only
`SECURITY_FINDING` and `EXPOSURE` can fail CI. `CAPABILITY` is inventory.
Decisions are `BLOCK` / `REVIEW` / `NO-GATED-FINDINGS` — never a numeric trust
score. Unparsed configs and `MANUAL_ONLY` surfaces are reported as coverage
gaps ([`docs/COVERAGE-MATRIX.md`](docs/COVERAGE-MATRIX.md)).

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
