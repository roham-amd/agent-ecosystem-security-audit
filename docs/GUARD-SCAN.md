# AESA Guard scan — operator guide

This document describes the Guard scan path current through **3.5.0**: deterministic
discovery plus evidence-backed security observations via `aesa scan`, with explicit
capability / exposure / finding separation. Default artifacts land in cwd
`./aesa-out` (not inside the target tree). Companion commands: `aesa doctor`
(host map) and `aesa vet` (pre-install verdict).

Companion docs: [`CLI-REFERENCE.md`](CLI-REFERENCE.md), [`SECURITY-RULES.md`](SECURITY-RULES.md), [`EVIDENCE-MODEL.md`](EVIDENCE-MODEL.md), [`POLICY.md`](POLICY.md).

---

## What Guard scan is

`aesa scan` answers, for a local repository tree:

1. What agent-ecosystem components exist?
2. What security-relevant **capabilities** do they appear to have?
3. Which **deterministic rules** fire, with file evidence?
4. What remains **NOT VERIFIED** (coverage gaps)?
5. What changed since a saved **baseline** (optional)?

It does **not**:

- Execute target code, install dependencies, or contact MCP/production endpoints
- Prove exploits or issue a global “secure/insecure” verdict
- Replace host IAM, network policy, or human risk acceptance
- Guarantee complete discovery (adapters have maturity levels)

---

## Hybrid responsibility model

```text
Repository (untrusted data)
        │
        ▼
┌───────────────────┐
│  aesa scan        │  Deterministic facts + OBSERVED/POTENTIAL findings
│  (Guard engine)   │
└─────────┬─────────┘
          │ aesa-out/
          ▼
┌───────────────────┐
│  Optional AI      │  Semantic review, modules, structured claims
│  (auditor skill)  │
└─────────┬─────────┘
          ▼
┌───────────────────┐
│  Human operator   │  Scope, acceptance, production decisions
└───────────────────┘
```

Principle: never ask an LLM to establish a fact the CLI can establish; never let an unsupported LLM claim become an enforced finding.

---

## First-run workflow (target: under 10 minutes)

```bash
cd tools && uv sync --locked
uv run aesa scan /path/to/target-repo
uv run aesa explain F-001 -o /path/to/target-repo/aesa-out   # if findings exist
uv run aesa baseline save -o /path/to/target-repo/aesa-out
```

Docker:

```bash
docker compose build
TARGET=/path/to/target-repo docker compose run --rm aesa \
  scan /work -o /work/aesa-out
```

---

## Pipeline internals

1. **Bounded inventory** — adapters walk the tree with file/depth/byte limits; refuse symlink escape; emit `inventory.json` + coverage matrix; attach content digests and fingerprints.
2. **Capability extraction** — map hints/types to capability kinds with explicit `origin` (`DECLARED` / `POTENTIAL` / `TYPE_DEFAULT`; never claim effective host permissions from type defaults alone).
3. **Rule engine** — apply versioned rules `AESA-RULE-001`…`010` classifying each hit as `CAPABILITY`, `EXPOSURE`, or `SECURITY_FINDING` (see [`SECURITY-RULES.md`](SECURITY-RULES.md)).
4. **Evidence registry** — each finding references evidence with path, optional line span, content digest, and audited commit when known.
5. **Reporting** — authority snapshot + Markdown + JSON + SARIF; `aesa explain` for one finding.
6. **Optional baseline delta** — fingerprint-aware comparison; CI `--fail-on` ignores pure capability observations.

---

## Output directory layout

```text
aesa-out/
├── inventory.json           # components + coverage.adapter_matrix
├── ecosystem-graph.json     # structural seed (not attack-path proof)
├── findings.json            # findings, evidence_registry, capabilities, summary
├── capabilities.json        # capabilities array
├── findings.sarif.json      # SARIF 2.1.0 for CI / code scanning upload
├── scan-summary.txt         # human terminal report
├── scan-report.md           # Markdown wrapper + executive questions
├── profile.json             # product/version/rules/limitations
├── baseline.json            # after `aesa baseline save` or `--save-baseline`
└── risk-delta.json          # when `--baseline` supplied
```

### Terminal report sections

- Ecosystem summary (component count, authority-bearing, external destinations, high-priority candidates)
- Components by type
- Findings (severity/confidence, evidence path, recommended action)
- Coverage / NOT VERIFIED
- Honesty footer (observations ≠ confirmed exploits)

### `findings.json` top-level fields

| Field | Meaning |
| --- | --- |
| `findings_version` | Guard findings document version (`1.0`) |
| `product` / `product_version` / `package_version` | AESA Guard identity |
| `repository` / `audited_commit` | Exact assessed tree |
| `rules_applied` | Rule ids executed |
| `summary` | Counts and severity histogram |
| `capabilities` | Extracted capability records |
| `evidence_registry` | Evidence objects |
| `findings` | Finding objects |
| `coverage` | From inventory |
| `limitations` | Explicit non-claims |

---

## Scan vs audit profiles

| Concern | `aesa scan` | `aesa audit --profile …` |
| --- | --- | --- |
| Deterministic findings | Yes | No (inventory + handoff only) |
| SARIF | Yes | Via separate export of a later report |
| Agent handoff Markdown | Minimal (`scan-report.md`) | Rich (`audit-context.md`, stage checklist, modules) |
| Deployment worksheet | No | `deployment` profile |
| Recommended first command | **Yes** | Use after scan for deep review |

You may run both: scan for security observations, then `audit --profile standard` for a structured deep-review package.

---

## Baselines and continuous assessment

1. First assessment: `aesa scan .` then `aesa baseline save -o aesa-out`.
2. After changes: `aesa scan . --baseline aesa-out/baseline.json`.
3. Inspect `risk-delta.json` for added HIGH/CRITICAL finding keys.
4. CI: set Action `fail-on: high` and pass `baseline` input (see [`aesa-consumer-gate.example.yml`](aesa-consumer-gate.example.yml)).

Baseline identity is **fingerprint-first** (content digest of authority-bearing
evidence), with path/name as a secondary signal. Renames of unchanged content
should not look like new risk; treat residual churn as a review signal, not
absolute truth.

---

## CI integration (AESA Guard Action)

Composite action: [`.github/actions/aesa-gate`](../.github/actions/aesa-gate).

| Input | Default | Notes |
| --- | --- | --- |
| `path` | `.` | Target path (passed via env, not shell-interpolated) |
| `mode` | `scan` | `scan` or legacy `audit` |
| `profile` | `quick` | Only for `mode=audit` |
| `baseline` | — | Guard `baseline.json` |
| `baseline-inventory` | — | Optional inventory path diff |
| `fail-on` | empty → policy / never | `never` \| `high` \| `any` |
| `trusted-policy` | `true` | Load `.aesa.yml` from PR base ref; fail on policy edits |
| `output-dir` | `aesa-out` | Artifact dir |
| `install-tools-from` | empty → Action-bundled tools | Prefer pinned kit; refuse accidental PR `./tools` |
| `upload-sarif` | `true` | Prints SARIF path for optional upload |

Hardening note: inputs are mapped to environment variables before bash uses them.
Never `uv sync` a PR-controlled `tools/` directory as the scanner.

---

## Optional AI deep review after scan

1. Attach [`../skills/aesa-auditor/SKILL.md`](../skills/aesa-auditor/SKILL.md).
2. Load [`../prompts/04-passive-guardrails.md`](../prompts/04-passive-guardrails.md).
3. Point the agent at `aesa-out/findings.json` and `inventory.json`.
4. Load only matching [`../modules/`](../modules/).
5. Require structured claims → `aesa validate claim`.
6. Produce narrative + audit-report JSON → `aesa validate report`.

---

## Honesty and common misreads

| Misread | Correct interpretation |
| --- | --- |
| “0 findings ⇒ safe” | Incomplete coverage; many risks need host/runtime evidence |
| “HIGH finding ⇒ CVE” | Static configuration observation / potential path |
| “Graph edge ⇒ exploit” | Structural seed only |
| “CI green ⇒ production OK” | Only the configured policy thresholds passed |

Always keep the four questions separate: discovery, component trust, integration trust, production suitability.
