# authdiff CLI reference

Primary command: **`authdiff`**. Compatibility alias: **`aesa`**.
Maintainer entry: **`authdiff-dev`** (build / lint / corpus / benchmark / …).

Package `aesa-tools` **0.11.0** · product **3.8.0**.

Product contract / command tiers: [`PRODUCT.md`](PRODUCT.md) ·
lock semantics: [`AUTHORITY-LOCK.md`](AUTHORITY-LOCK.md).

Install: [`INSTALL.md`](INSTALL.md).

---

## Product command overview

| Command | Purpose |
| --- | --- |
| `lock` | Write / update / `--check` `AUTHORITY.lock` (north-star artifact) |
| `doctor` | Host authority map (Cursor / Claude / VS Code / …) |
| `vet` / `open` | Pre-install verdict for a local path or GitHub URL |
| `ci init` / `init-gate` | Write `.aesa.yml` + workflow + CODEOWNERS stub |
| `scan` / `check` | Repo Guard findings + SARIF (add `--locked`, `--full`) |
| `delta` | New-only authority gate vs `--baseline` |
| `harden` / `fix` | Dry-run least-privilege patch proposals |
| `explain` | Detailed explanation of a finding id |
| `baseline` | Save / show finding baselines (complements lock; different contract) |
| `annotate` | GitHub annotations or Authority Diff PR comment |
| `diff lock` | Record-level diff of two `AUTHORITY.lock` files |
| `diff risk` | Finding risk delta vs baseline |
| `init-manifest` / `verify-manifest` | Experimental declared-vs-observed `AUTHORITY.yml` |
| `run` / `snapshot` / `artifact-vet` / `atlas` / `lsp-validate` | Opt-in advanced |

Maintainer-only (`authdiff-dev`): `build`, `lint`, `deps`, `corpus`, `benchmark`,
`pilots`, `hosts`, `validate`, `graph`, `inventory`, `audit`, `preflight`, `verify`,
`export`.

---

## `aesa doctor`

```bash
aesa doctor [--home PATH] [-o OUTPUT_DIR] [--fail-on never|high|any] [--agent]
```

Reads local host configs under the user home (`~/.cursor`, `~/.claude`,
`~/.mcp.json`, `~/.vscode`, `~/.codex`). Local-only; nothing is uploaded.
Lone config files are staged redacted under a throwaway dir (never copied raw
into `-o`). `$HOME` is never scanned wholesale. `--agent` needs `-o` so surface
`findings.json` files remain available.

---

## `aesa vet`

```bash
aesa vet SOURCE [-o OUTPUT_DIR] [--keep-clone] [--agent]
```

`SOURCE` is a local path, Git URL, or `owner/repo` GitHub shorthand. Remote
sources are shallow-cloned with hooks disabled, no submodules, and no LFS
smudge. Exit `0` = `NO_FINDINGS_IN_SCOPE`; `1` = review/reject (incl. unparsed
configs); `2` = tooling failure (e.g. missing `git`). `--agent` prints a fenced
JSON digest.

---

## `authdiff lock`

```bash
authdiff lock [PATH] [--check] [--update] [--lock-file PATH]
```

Writes a sorted `AUTHORITY.lock` (v2) of authority records. `--check` regenerates
and exits `1` on drift (same as `authdiff check --locked`). Protect the file with
CODEOWNERS; prefer this over long-term reliance on suppressions alone.

## `authdiff ci init` / `init-gate`

```bash
authdiff ci init [PATH] [--force]
```

Writes `.aesa.yml`, `.github/workflows/aesa-gate.yml`, and `.github/CODEOWNERS`
(placeholder `@YOUR_TEAM` for `AUTHORITY.lock`). Does not overwrite unless `--force`.

---

## `aesa harden`

```bash
aesa harden [--findings PATH] [--apply]
```

Reads a prior `findings.json` and prints dry-run least-privilege patch templates
for high-confidence gated rules. `--apply` is rejected (exit `2`) in this
release — patches are never written automatically.

---

## `aesa init-manifest` / `aesa verify-manifest`

```bash
aesa init-manifest [PATH] [--force]
aesa verify-manifest [PATH] [-o REPORT.json]
```

`init-manifest` drafts `AUTHORITY.yml` from observed inventory (declared vs
observed). `verify-manifest` fails when undeclared components appear. Matching
a declaration is **not** a security clearance.

---

## `aesa scan`

One-command Guard assessment of a repository tree.

```bash
aesa scan [PATH] [-o OUTPUT_DIR] [--baseline PATH] [--save-baseline PATH]
         [--fail-on never|high|any] [--policy PATH] [--no-policy] [--agent]
```

| Argument | Default | Description |
| --- | --- | --- |
| `PATH` | `.` | Target repository root (read-only traversal) |
| `-o` / `--output-dir` | `./aesa-out` (cwd) | Artifact directory (not under target by default) |
| `--baseline` | — / `.aesa.yml` | Prior `baseline.json` for risk delta |
| `--save-baseline` | — | Write baseline after scan |
| `--fail-on` | `never` or `.aesa.yml` | Exit `1` when policy matches |
| `--policy` | `.aesa.yml` inside scan target only | Explicit policy path (never parent dirs outside target) |
| `--no-policy` | off | Ignore `.aesa.yml` |
| `--agent` | off | Print compact fenced agent digest (+ write `agent-digest.json`) |

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success (or findings present but policy `never`) |
| `1` | Policy failure (`high` / `any`) |
| `2` | CLI usage error |

### Artifacts written

| File | Description |
| --- | --- |
| `inventory.json` | Discovered components + coverage |
| `ecosystem-graph.json` | Structural graph seed |
| `findings.json` | Guard findings, evidence registry, capabilities |
| `capabilities.json` | Capability extraction subset |
| `findings.sarif.json` | SARIF 2.1.0 |
| `scan-summary.txt` | Terminal report (also printed) |
| `scan-report.md` | Markdown summary |
| `pr-comment.md` | ≤12-line Authority Diff PR comment |
| `profile.json` | Scan metadata + rules applied |
| `risk-delta.json` | Only when `--baseline` is provided |
| `agent-digest.json` | Only when `--agent` is set |

Details: [`GUARD-SCAN.md`](GUARD-SCAN.md), rules: [`SECURITY-RULES.md`](SECURITY-RULES.md).

### Examples

```bash
aesa scan .
aesa scan /repos/app -o /tmp/aesa-out --fail-on high
aesa scan . --baseline aesa-out/baseline.json --save-baseline aesa-out/baseline.json
```

---

## `aesa explain`

```bash
aesa explain FINDING_ID [-o OUTPUT_DIR] [--agent]
```

Reads `OUTPUT_DIR/findings.json` (default `aesa-out`) and prints attack-path reasoning, evidence, missing controls, and recommended action for `F-001`, etc. `--agent` emits structured remediation JSON with fenced evidence strings.

---

## `aesa baseline`

```bash
aesa baseline save [-o OUTPUT_DIR] [--path BASELINE.json]
aesa baseline show [BASELINE.json]
```

`save` re-scans the repository recorded in `findings.json` (or uses the output dir parent) and writes a baseline of component keys + finding keys for future risk deltas.

Default baseline path: `<output-dir>/baseline.json`.

---

## `aesa audit`

```bash
aesa audit [PATH] [--profile quick|standard|deployment] [-o OUTPUT_DIR]
```

| Profile | Purpose | Deep review handoff | Deployment worksheet |
| --- | --- | --- | --- |
| `quick` | Inventory + prioritization | No | No |
| `standard` | Deeper agent handoff (default) | Yes | No |
| `deployment` | Production suitability worksheet | Yes | Yes |

### Artifacts

`inventory.json`, `ecosystem-graph.json`, `audit-context.md`, `audit-summary.md`, `preflight-summary.md`, `profile.json`, and optionally `deployment-worksheet.md`.

Prefer **`aesa scan`** for security observations; use **`audit`** when preparing an AI agent deep-review package.

---

## `aesa preflight`

```bash
aesa preflight [PATH] [-o OUTPUT_DIR]
```

Alias of `aesa audit --profile quick` (2.3 compatibility).

---

## `aesa inventory`

```bash
aesa inventory PATH [-o OUTPUT.json]
```

Passive discovery only. Prints JSON to stdout unless `-o` is set.

---

## `aesa validate`

```bash
aesa validate report PATH [--no-semantic]
aesa validate graph PATH [--no-semantic]
aesa validate claim PATH
```

| Subcommand | Checks |
| --- | --- |
| `report` | JSON Schema + semantic refs (evidence ids, component ids) |
| `graph` | Graph schema + semantic edge/node consistency |
| `claim` | Structured claim object; `CONFIRMED` requires non-empty `evidence_ids` |

Exit `0` on OK, `1` on validation failure.

---

## `aesa graph paths`

```bash
aesa graph paths PATH.json
```

Prints auto-discovered structural path candidates from an ecosystem graph JSON. Paths are **not** confirmed attack proofs.

---

## `aesa diff`

```bash
aesa diff report BASE.json TARGET.json
aesa diff graph BASE.json TARGET.json
aesa diff risk BASELINE.json FINDINGS.json
```

| Kind | Compares |
| --- | --- |
| `report` | Component / finding id sets and severity/title changes |
| `graph` | Edge keys added/removed |
| `risk` | Guard baseline vs current findings (prefer re-scan when repo path exists) |

---

## `aesa export sarif`

```bash
aesa export sarif REPORT_OR_FINDINGS.json [-o OUT.sarif.json]
```

Accepts audit-report JSON or Guard `findings.json`. Tool name in SARIF: **AESA Guard**.

Note: `aesa scan` already writes `findings.sarif.json`.

---

## `aesa annotate`

```bash
aesa annotate [FINDINGS.json] [--format github|text|pr-comment] [--risk-delta PATH]
```

| Argument | Default | Description |
| --- | --- | --- |
| `FINDINGS.json` | `aesa-out/findings.json` | Guard findings document |
| `--format` | `github` | `github` = Actions workflow commands; `text` = plain lines; `pr-comment` = ≤12-line Authority Diff |
| `--risk-delta` | — | Optional `risk-delta.json` for delta-first PR comments |

`github`/`text` emit annotations only for `SECURITY_FINDING` / `EXPOSURE` (never pure `CAPABILITY`). Target-derived strings in `pr-comment` are markdown-escaped. The GitHub Action runs annotations after scan when `annotate: true` and posts the Authority Diff comment to the job summary.

---

## `aesa pilots`

```bash
aesa pilots list [--manifest PATH]
aesa pilots run [--manifest PATH] [-o OUT_DIR] [--only ID ...]
```

Runs curated adoption scans from [`archive/pilots/manifest.json`](archive/pilots/manifest.json)
(`authdiff-dev pilots`). Pilot results are **not** AgentSecBench external evidence.
See [`archive/pilots/README.md`](archive/pilots/README.md).

---

## `aesa verify`

```bash
aesa verify digest PATH [--expected HEX]
aesa verify manifest PATH [-o OUT.json]
```

Passive SHA-256 helpers. See [`../tools/aesa/supply_chain/README.md`](../tools/aesa/supply_chain/README.md).

---

## `aesa build`

```bash
aesa build [all|schemas|prompts] [--write]
```

| Target | Behavior |
| --- | --- |
| `all` | Schema parity, version metadata, dependency pins, example validation, monolith check |
| `schemas` | Copy canonical audit-report schema to published aliases |
| `prompts` | Check or (`--write`) regenerate `archive/methodology/prompts/audit.full.md` |

---

## `aesa hosts`

```bash
aesa hosts list
aesa hosts show cursor
aesa hosts show claude-code
```

Lists built-in host assessment profiles. Profiles describe **declared** configuration surfaces; effective permissions remain NOT VERIFIED without host/runtime evidence.

---

## `aesa corpus` / `aesa benchmark`

```bash
aesa corpus run
aesa benchmark run
aesa benchmark rules
aesa benchmark governance
aesa benchmark contract verify
aesa benchmark submitter-package -o DIR
aesa benchmark intake DIR --agent-id ID [--provenance external|pilot|sample|template] [--dry-run]
aesa benchmark intakes
aesa benchmark collection-status
aesa benchmark llm --validate-only [--split public|held_out|all]
aesa benchmark llm --submissions DIR [--split …] [--report] [--provenance external|any|…]
```

- **Corpus:** deterministic tooling regression (`tests/corpus/`, CORPUS-001…010).
- **`benchmark run`:** inventory + Guard rule smoke cases (`tests/benchmark/cases`).
- **`benchmark rules`:** per-rule positive/negative/ambiguous quality pack (`tests/rules/`).
- **`benchmark governance`:** LLM dataset checksums and version pins.
- **`benchmark contract`:** frozen evaluation contract verification.
- **`benchmark submitter-package`:** task cards without ground truth for external submitters.
- **`benchmark intake` / `intakes`:** validate, checksum, and preserve submissions as untrusted data (never execute); list external evidence.
- **`benchmark collection-status`:** invitations vs responses vs valid intakes (zeros until outreach yields evidence).
- **`benchmark llm`:** offline scoring / transparent report (never calls model APIs). Templates/pilots are not external evidence.

Exit `0` if all cases pass, `1` otherwise.

---

## `aesa deps`

```bash
aesa deps outdated
aesa deps upgrade [--dry-run]
```

Compares / refreshes `tools/uv.lock` against PyPI. Does not rewrite human constraints in `pyproject.toml` except via normal `uv` workflows.

---

## `aesa lint`

```bash
aesa lint [--fix] [--format] [--check-format]
```

Runs Ruff on `tools/aesa` and `tests`.

---

## Library entry points

| Symbol | Module |
| --- | --- |
| `run_scan` | `aesa.security.scan` |
| `run_security_scan` | `aesa.security.engine` |
| `run_audit` | `aesa.audit` |
| `collect_inventory` | `aesa.inventory.collector` |
| `product_version` | `aesa.versioning` |

---

## Related docs

- [`GUARD-SCAN.md`](GUARD-SCAN.md)
- [`../tools/README.md`](../tools/README.md)
- [`AESA-GATE.md`](AESA-GATE.md)
- [`.github/actions/aesa-gate/action.yml`](../.github/actions/aesa-gate/action.yml)
