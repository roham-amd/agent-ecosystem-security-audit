# AESA Guard CLI reference

Complete reference for the `aesa` console script (package `aesa-tools` **0.6.1**).

Install:

```bash
cd tools
uv sync --locked
uv run aesa --help
```

Entry points: `aesa` (console script) and `python -m aesa`.

---

## Command overview

| Command | Purpose |
| --- | --- |
| `scan` | **Primary.** Inventory + deterministic Guard findings + SARIF |
| `explain` | Print detailed explanation of a finding id |
| `baseline` | Save / show recurring assessment baselines |
| `audit` | Profile-based inventory + AI agent handoff package |
| `preflight` | Alias of `audit --profile quick` |
| `inventory` | Inventory JSON only |
| `validate` | Validate report, graph, or structured claim |
| `graph paths` | List auto-discovered graph attack-path candidates |
| `diff` | Diff reports, graphs, or Guard risk vs baseline |
| `export sarif` | Export findings / report to SARIF 2.1.0 |
| `verify` | Digest verify / digest manifest |
| `build` | Schema sync, monolith, version consistency |
| `corpus` | Tooling regression corpus |
| `benchmark` | AgentSecBench detection fixtures |
| `deps` | Lock outdated / upgrade helpers |
| `lint` | Ruff lint / format |

---

## `aesa scan`

One-command Guard assessment.

```bash
aesa scan [PATH] [-o OUTPUT_DIR] [--baseline PATH] [--save-baseline PATH] [--fail-on never|high|any]
```

| Argument | Default | Description |
| --- | --- | --- |
| `PATH` | `.` | Target repository root (read-only traversal) |
| `-o` / `--output-dir` | `<PATH>/aesa-out` | Artifact directory |
| `--baseline` | — | Prior `baseline.json` for risk delta |
| `--save-baseline` | — | Write baseline after scan |
| `--fail-on` | `never` | Exit `1` when policy matches |

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
| `profile.json` | Scan metadata + rules applied |
| `risk-delta.json` | Only when `--baseline` is provided |

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
aesa explain FINDING_ID [-o OUTPUT_DIR]
```

Reads `OUTPUT_DIR/findings.json` (default `aesa-out`) and prints attack-path reasoning, evidence, missing controls, and recommended action for `F-001`, etc.

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
| `prompts` | Check or (`--write`) regenerate `prompts/audit.full.md` |

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
