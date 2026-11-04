# AESA Guard policy file (`.aesa.yml`)

Repository-level defaults for the Guard scan and CI gate.

| Item | Value |
| --- | --- |
| Contract | **1.1** |
| Discovery | Look for `.aesa.yml` **inside the scan target tree only** (never parent dirs outside the target) |
| CI trust | Action `trusted-policy=true` loads `.aesa.yml` from the **PR base ref** and fails if the PR edits policy |
| Override | Explicit CLI flags always win |
| Disable | `aesa scan --no-policy` |

## Example

```yaml
version: 1

policy:
  mode: enforce          # advisory | enforce
  fail_on: high          # never | high | any
  output_dir: aesa-out
  baseline: .aesa/baseline.json

  require_review:
    - remote_mcp_endpoint
    - privileged_hook
    - credential_access
    - unattended_execution

  ignore:
    - rule: AESA-RULE-003
      path: examples/**
      justification: "Non-production fixture"
      owner: security-team
      expires: "2027-01-01"
```

Committed example: [`../examples/aesa.policy.example.yml`](../examples/aesa.policy.example.yml).

## Semantics

| Field | Behavior |
| --- | --- |
| `mode: enforce` | If `fail_on` is omitted or `never`, Guard raises it to `high` |
| `mode: advisory` | Does not change exit policy by itself |
| `fail_on: high` | Exit 1 on CRITICAL/HIGH `SECURITY_FINDING` or `EXPOSURE` (never pure `CAPABILITY`) |
| `fail_on: any` | Exit 1 on any `SECURITY_FINDING` or `EXPOSURE` |
| `ignore` | Suppress matching findings before gating; each entry **requires** `justification` |
| `ignore[].expires` | Optional `YYYY-MM-DD`; expired suppressions are ignored (fail closed) |
| `require_review` | Recorded in scan payload for humans/reviewers; does not auto-fail yet |

Gate classes are centralized in `tools/aesa/security/gating.py`: only
`SECURITY_FINDING` and `EXPOSURE` can block. `CAPABILITY` never blocks under
`fail_on=high|any`, including baseline risk deltas (`gated_findings_added`).

## Finding lifecycle (gates)

| Class | Default CI gate |
| --- | --- |
| `CAPABILITY` | Never blocks unless you build a custom consumer |
| `EXPOSURE` | Blocks under `fail_on: high` when severity is HIGH/CRITICAL, or under `any` |
| `SECURITY_FINDING` | Same as exposure |

Suppressions must not become permanent blind spots: require owner, justification, and preferably an expiration date.

## CLI

```bash
uv run aesa scan . --policy .aesa.yml --fail-on high
uv run aesa scan . --no-policy
```

## Gate integrity

A policy file that the PR author can edit is not a gate. In CI:

1. Set Action input `trusted-policy: true` (default).
2. Checkout with enough history to read the base ref (e.g. `fetch-depth: 0`).
3. Pin AESA tools via `install-tools-from: .aesa-kit/tools` (or rely on
   Action-bundled tools). Do not let a PR supply the scanner under `./tools`.
4. Treat PR edits to `.aesa.yml` as their own authority-surface change (the
   Action fails closed on those edits when `trusted-policy` is enabled).
