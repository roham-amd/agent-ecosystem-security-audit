# Recipe — Guard-first assessment (recommended default)

Use this pattern for most repositories that may contain Skills, MCP configs, hooks, or other agent surfaces.

## Goal

Produce evidence-backed security observations in under 10 minutes, then optionally deepen with an AI auditor.

## Steps

1. **Authorize scope** — confirm repository path/commit, data sensitivity, and that passive mode is required.
2. **Scan**
   ```bash
   cd tools && uv sync --locked
   uv run aesa scan /path/to/target -o /path/to/work/aesa-out
   ```
3. **Triage** — read `scan-summary.txt`; open HIGH/CRITICAL findings with `aesa explain F-00N`.
4. **Baseline** — `aesa baseline save -o …/aesa-out` for future diffs.
5. **Deep review (optional)** — attach `skills/aesa-auditor` + `prompts/04-passive-guardrails.md`; load only matching modules.
6. **Claims** — require structured claims; `aesa validate claim`.
7. **Report** — narrative + JSON; `aesa validate report`.
8. **Govern** — wire CI Action with `fail-on: high` and the saved baseline.

## Expected outputs

- Deterministic findings with file evidence
- Explicit NOT VERIFIED coverage gaps
- Optional validated audit-report JSON after deep review

## Non-goals

- Declaring the repository “secure”
- Executing target code or contacting MCP endpoints in passive mode

See also: [`../GUARD-SCAN.md`](../GUARD-SCAN.md), [`small-repo-deep-audit.md`](small-repo-deep-audit.md).
