# AESA Guard — short primer

AESA Guard is an **Authority Diff** for AI agents: local discovery, deterministic
security observations, and a CI-oriented change gate.

| Item | Value |
| --- | --- |
| Product release | **3.6.1** |
| Procedure | **1.0** |
| Tooling package | **0.8.1** (`aesa-tools`) |
| Rule pack | **1.3** |
| Rule pack | **1.2** |
| Primary path | `aesa doctor` → `aesa vet` → `aesa init-gate` → `aesa scan` |
| Policy file | `.aesa.yml` (optional; trusted from PR base ref in CI) |

Normative depth: [`GUARD-SCAN.md`](GUARD-SCAN.md), [`POLICY.md`](POLICY.md),
[`DOCUMENTATION-INDEX.md`](DOCUMENTATION-INDEX.md).

---

## Job to be done

> Before I install, merge, deploy, or upgrade an AI-agent integration, tell me
> what authority it introduces, who receives that authority, what data can flow
> through it, and what materially changed.

1. **Discover** — Skills, MCP registrations, hooks, plugins, subagents, automations, host configs, CI workflows.
2. **Assess** — Deterministic Guard rules + optional evidence-bounded AI/human review.
3. **Govern** — Baselines, risk diffs, trusted CI policy, SARIF.

---

## Execution model (hybrid)

| Role | Responsibility | Final decision |
| --- | --- | --- |
| Deterministic tools (`doctor` / `vet` / `scan`) | Inventory, capabilities, rules, evidence, baselines, SARIF | No |
| AI audit agent | Semantics, complex attack paths, explanations | No |
| Human operator | Scope, risk acceptance, runtime authorization | Yes |

Never ask an LLM to establish a fact a deterministic tool can establish.  
Never let an unsupported LLM interpretation become an enforced finding.

---

## First user journey

```bash
uv tool install git+https://github.com/roham-amd/agent-ecosystem-security-audit.git@v3.6.1#subdirectory=tools

aesa doctor                          # host authority map
aesa vet github.com/org/some-skill   # pre-install verdict
aesa init-gate                       # .aesa.yml + workflow stub
aesa scan .
aesa explain F-001 -o aesa-out
```

CI: [`.github/actions/aesa-gate`](../.github/actions/aesa-gate) with
`trusted-policy: true`, pinned kit, `fail-on: high`.  
Example: [`aesa-consumer-gate.example.yml`](aesa-consumer-gate.example.yml).

`aesa audit --profile …` remains for agent handoff packages only.

Guard never prints a global “secure” / “insecure” verdict. It reports
observations, coverage, and unknowns. `NO FINDINGS` on `PARTIAL` /
`MANUAL_ONLY` surfaces is not a clearance.

---

## Interfaces

| Interface | Status |
| --- | --- |
| CLI (`doctor` / `vet` / `scan`) | Primary product |
| GitHub Action (trusted policy) | Supported (composite) |
| AI agent skill | Supported (`skills/aesa-auditor`, self-contained) |
| Prompt-only kit | Optional deep assessment |
| MCP server assistant | Deferred |
| Web workbench / marketplace | Deferred |

---

## Non-goals (for now)

- Marketplace “certified secure” badges
- SaaS multi-tenant evidence storage
- Bundled runtime detonation harness
- Numeric trust scores that hide coverage gaps
- Claiming LLM detection accuracy without external AgentSecBench intakes (N=0)
