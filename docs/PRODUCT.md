# authdiff product contract

**Product:** `authdiff` — Authority Diff for AI agents  
**Release:** 3.8.0 · **Package:** `aesa-tools` 0.11.0 · **Lock:** v2  

This page freezes what the product is, what it is not, and which commands are
primary. Historical AESA methodology lives under [`archive/`](../archive/).

---

## North star

> Know what authority your AI agents gain, before install and on every pull request.

The real product is an **authority-change control**, not an audit framework, not
a prompt library, and not a generic vulnerability scanner.

One question drives the workflow:

> What new authority did this AI-agent change introduce, and who approved it?

---

## Naming (AESA vs authdiff)

| Name | Role |
| --- | --- |
| **authdiff** | Current product name and primary CLI |
| **AESA** / AESA Guard | Former brand; retained in package/path compatibility |
| `aesa` | Compatibility CLI alias for `authdiff` |
| `aesa-tools` | PyPI / import package name |
| `.aesa.yml` | Policy file (compatibility name; not a second product) |
| `aesa-out/` | Default artifact directory |
| `.github/actions/aesa-gate` | GitHub Action path (display name: authdiff) |
| `skills/aesa-auditor` | Thin agent skill that **explains** CLI evidence |

AESA and authdiff are the **same product line** under a renamed identity.
`authdiff` is canonical in operator docs; AESA names remain for install paths
and committed policy files.

---

## Primary mental model (three questions)

1. **What authority do I already have?** → `authdiff doctor` / `authdiff`
2. **What authority does this change introduce?** → `authdiff open` / lock diff / PR comment
3. **Is that change approved?** → `AUTHORITY.lock` + CODEOWNERS + CI gate

Everything else is secondary.

---

## Core command tier

| Tier | Commands |
| --- | --- |
| **Core** | `authdiff` (default scan), `doctor`, `open`/`vet`, `lock`, `ci init`, `check --locked` |
| **Review** | `explain`, `diff lock`, `delta`, `annotate`, `fix`/`harden` |
| **Advanced / opt-in** | `run`, `snapshot`, `artifact-vet`, `atlas`, `lsp-validate`, manifests |
| **Maintainer** | `authdiff-dev` only (`build`, `lint`, `corpus`, `benchmark`, …) |

---

## Claims boundary

authdiff **does**:

- Inventory supported agent-related components and configuration
- Identify declared or potential capabilities
- Find risky patterns with deterministic rules
- Preserve evidence that explains why a finding exists
- Detect changes against `AUTHORITY.lock`
- Produce outputs for developers, reviewers, and CI

authdiff **does not**:

- Prove a component is safe or certify skills / MCP servers
- Sandbox agents or replace host IAM
- Prove exploitability merely because a capability exists
- Guarantee complete discovery of all agent-related authority
- Let an AI agent approve policy or promote claims to `CONFIRMED` without evidence IDs

A clean scan means: **nothing risky was detected in the supported subset**, with
coverage gaps listed. It is never a clearance.

---

## Hybrid responsibility

| Role | Responsibility |
| --- | --- |
| Scanner + adapters | Observable facts, parsing, hashes, inventory |
| Deterministic rules | Reproducible findings + explicit uncertainty |
| Authority engine | Normalize, lock, diff, classify changes |
| AI agent (optional) | Explain evidence, propose remediation |
| Human reviewer | Accept risk, approve authority, own policy |

Deterministic tooling is the source of truth. AI is an optional explainer.

---

## Success metrics (what we optimize)

| Dimension | Metric |
| --- | --- |
| Activation | Time to first meaningful authority map &lt; 2 minutes |
| Activation | Time to first CI integration &lt; 10 minutes |
| Quality | Gated findings always cite evidence references |
| Coverage | Every scan exposes unsupported / unparsed surfaces when applicable |
| Trust | Zero `CONFIRMED` without independent evidence IDs |
| UX | Default PR comment ≤ 12 lines |
| Security | Zero target code execution during passive inspection |

Do **not** optimize for stars, rule count, or number of output files.

---

## Deferred (intentionally)

Local web viewer, MCP audit server, marketplace / certification, SaaS dashboard,
and runtime capability firewalls are **out of the current commitment**. See
[`archive/RADICAL-ALTERNATIVES.md`](archive/RADICAL-ALTERNATIVES.md).

---

## Related contracts

| Doc | Contract |
| --- | --- |
| [`AUTHORITY-LOCK.md`](AUTHORITY-LOCK.md) | Lock semantics, identity, diff classes |
| [`COVERAGE-MATRIX.md`](COVERAGE-MATRIX.md) | Adapter maturity / unknowns |
| [`EVIDENCE-MODEL.md`](EVIDENCE-MODEL.md) | Evidence honesty + chain of custody |
| [`AESA-GATE.md`](AESA-GATE.md) | CI gate + trusted policy |
| [`../schemas/authority-lock.schema.json`](../schemas/authority-lock.schema.json) | Machine schema |
