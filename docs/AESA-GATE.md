# AESA Gate — product direction

AESA Gate is the 2.3+ product identity for this repository.

## Job to be done

Help teams **discover**, **evidence**, and **gate change** in AI agent ecosystems — without claiming false assurance.

1. **Discover** — Skills, MCP registrations, hooks, plugins, subagents, automations, instruction rules, A2A cards.
2. **Assess** — Evidence-bounded component and integration review (AI agent + human).
3. **Control change** — Diff / CI-oriented posture change (roadmap); preflight is the local entry point today.

## Execution model (hybrid)

| Role | Responsibility | Final decision |
| --- | --- | --- |
| Deterministic tools (`aesa`) | Inventory, limits, graph seed, validate, diff, SARIF | No |
| AI audit agent | Semantics, attack paths, findings drafting | No |
| Human operator | Scope, risk acceptance, runtime authorization | Yes |

## First user journey

```bash
aesa preflight .
# → aesa-out/inventory.json + audit-context.md
# → load skills/aesa-auditor + matching modules/
# → aesa validate report summary.json
```

Preflight must never print “secure” / “insecure” as a global verdict. It reports coverage and unknowns.

## Near-term roadmap (condensed)

- Harden collectors and expand adapters with explicit `SUPPORTED` / `PARTIAL` / `MANUAL_ONLY` maturity.
- Ship Cursor / Claude Code skill workflows (done: `skills/`).
- GitHub Action PR gate for security-impactful ecosystem diffs (next).
- Benchmark corpus for agent audit quality (long-term; separate from tooling corpus).

## Non-goals (for now)

- Competing as a regex MCP scanner
- Marketplace “certified secure” badges
- SaaS multi-tenant evidence storage
- Bundled runtime detonation harness
