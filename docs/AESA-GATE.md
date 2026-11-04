# AESA Guard — short primer

AESA Guard is the operator-facing product name for AESA’s local discovery,
deterministic security observations, and CI-oriented change gate.

| Item | Value |
| --- | --- |
| Product release | **3.4.0** |
| Procedure | **1.0** |
| Tooling package | **0.7.0** |
| Primary command | `aesa scan` |
| Policy file | `.aesa.yml` (optional) |

Normative depth: [`AESA-3.0-PRODUCT-SPEC.md`](AESA-3.0-PRODUCT-SPEC.md), [`GUARD-SCAN.md`](GUARD-SCAN.md), [`DOCUMENTATION-INDEX.md`](DOCUMENTATION-INDEX.md).

---

## Job to be done

Help teams **discover**, **evidence**, and **gate change** in AI agent ecosystems —
without claiming false assurance.

1. **Discover** — Skills, MCP registrations, hooks, plugins, subagents, automations, instruction rules, A2A cards, CI workflows.
2. **Assess** — Deterministic Guard rules + optional evidence-bounded AI/human review.
3. **Govern** — Baselines, risk diffs, CI fail policies, SARIF.

Essential questions:

1. What can my agents access and execute?
2. Who or what grants those capabilities?
3. Where can data and authority flow?
4. What changed?
5. What is unsafe, unverified, or excessive?
6. What should I do about it?

---

## Execution model (hybrid)

| Role | Responsibility | Final decision |
| --- | --- | --- |
| Deterministic tools (`aesa scan`) | Inventory, capabilities, rules, evidence, baselines, SARIF | No |
| AI audit agent | Semantics, complex attack paths, explanations | No |
| Human operator | Scope, risk acceptance, runtime authorization | Yes |

Never ask an LLM to establish a fact a deterministic tool can establish.  
Never let an unsupported LLM interpretation become an enforced finding.

Evidence model: [`EVIDENCE-MODEL.md`](EVIDENCE-MODEL.md).  
Rules: [`SECURITY-RULES.md`](SECURITY-RULES.md).  
CLI: [`CLI-REFERENCE.md`](CLI-REFERENCE.md).

---

## First user journey

```bash
cd tools && uv sync --locked
uv run aesa scan .
uv run aesa explain F-001 -o aesa-out
uv run aesa baseline save -o aesa-out
# optional deep review via skills/aesa-auditor
```

CI: [`.github/actions/aesa-gate`](../.github/actions/aesa-gate) (`mode: scan`, `fail-on: high|any`, baseline risk delta).  
Example workflow: [`aesa-consumer-gate.example.yml`](aesa-consumer-gate.example.yml).

`aesa audit --profile …` remains for agent handoff packages.  
`aesa preflight` remains as an alias of `aesa audit --profile quick`.

Guard must never print a global “secure” / “insecure” verdict. It reports
observations, coverage, and unknowns.

---

## Interfaces

| Interface | Status |
| --- | --- |
| CLI (`aesa`) | Primary product |
| GitHub Action | Supported (composite) |
| AI agent skill | Supported (`skills/aesa-auditor`) |
| Prompt-only kit | Secondary distribution |
| MCP server assistant | Deferred |
| Web workbench / marketplace | Deferred |

---

## Non-goals (for now)

- Marketplace “certified secure” badges
- SaaS multi-tenant evidence storage
- Bundled runtime detonation harness
- Numeric trust scores that hide coverage gaps
- Claiming LLM detection accuracy without AgentSecBench model runners
