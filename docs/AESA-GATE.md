# AESA Gate — short primer

AESA Gate is the operator-facing name for AESA’s local discovery + CI-oriented change gate. Normative product contract: [`AESA-3.0-PRODUCT-SPEC.md`](AESA-3.0-PRODUCT-SPEC.md) (release **3.0.0**).

## Job to be done

Help teams **discover**, **evidence**, and **gate change** in AI agent ecosystems — without claiming false assurance.

1. **Discover** — Skills, MCP registrations, hooks, plugins, subagents, automations, instruction rules, A2A cards, CI workflows.
2. **Assess** — Evidence-bounded component and integration review (AI agent + human).
3. **Control change** — Baseline inventory, diff, optional GitHub Action.

## Execution model (hybrid)

| Role | Responsibility | Final decision |
| --- | --- | --- |
| Deterministic tools (`aesa`) | Inventory, limits, graph seed, validate, diff, SARIF | No |
| AI audit agent | Semantics, attack paths, findings drafting | No |
| Human operator | Scope, risk acceptance, runtime authorization | Yes |

## First user journey

```bash
aesa audit . --profile quick
# → aesa-out/inventory.json + audit-context.md + profile.json
# → load skills/aesa-auditor + matching modules/
aesa audit . --profile standard   # deeper handoff checklist
# → aesa validate report summary.json
```

**Docker + AI agent:** build the kit image, mount the target, run `aesa audit`, then hand
`aesa-out/` to Cursor / Claude Code / Codex / Antigravity (or similar). Step-by-step:
[`docker-agent-audit.md`](docker-agent-audit.md).

`aesa preflight` remains as an alias of `aesa audit --profile quick`.

Preflight/audit must never print “secure” / “insecure” as a global verdict. It reports coverage and unknowns.

## Near-term roadmap

- Expand adapters with explicit `SUPPORTED` / `PARTIAL` / `MANUAL_ONLY` maturity (ongoing).
- Cursor / Claude Code skill workflows (`skills/`).
- Consumer GitHub Action (`.github/actions/aesa-gate`).
- Benchmark corpus for agent audit quality (`aesa benchmark run` scaffold; LLM scoring next).

## Non-goals (for now)

- Competing as a regex MCP scanner
- Marketplace “certified secure” badges
- SaaS multi-tenant evidence storage
- Bundled runtime detonation harness
