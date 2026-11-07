# authdiff — CI Authority Diff gate

Product primer for the PR gate. Full product contract: [`PRODUCT.md`](PRODUCT.md).

| Item | Value |
| --- | --- |
| Product release | **3.8.0** |
| Tooling package | **0.11.0** (`aesa-tools`) |
| Rule pack | **1.4** |
| Primary path | `authdiff lock` → `ci init` → `check --locked` |
| Policy file | `.aesa.yml` (compat name) + `AUTHORITY.lock` (CODEOWNERS) |
| Action | `.github/actions/aesa-gate` (display name: authdiff) |

Normative depth: [`AUTHORITY-LOCK.md`](AUTHORITY-LOCK.md), [`GUARD-SCAN.md`](GUARD-SCAN.md),
[`POLICY.md`](POLICY.md), [`DOCUMENTATION-INDEX.md`](DOCUMENTATION-INDEX.md).

---

## Job to be done

> Before I install, merge, deploy, or upgrade an AI-agent integration, tell me
> what authority it introduces, who receives that authority, what data can flow
> through it, and what materially changed.

The valuable artifact is the **PR Authority Diff comment** (≤12 lines), answering:

1. What changed?
2. What new authority?
3. What evidence?
4. What is unknown?
5. What action is required?

---

## First user journey

```bash
uvx --from "git+https://github.com/roham-amd/agent-ecosystem-security-audit.git@v3.8.0#subdirectory=tools" authdiff
# Prefer when published: pip install aesa-tools==0.11.0

authdiff doctor                          # host authority map
authdiff open github.com/org/some-skill  # pre-install verdict
authdiff                                 # ≤15-line authority map
authdiff lock                            # write AUTHORITY.lock
authdiff ci init                         # .aesa.yml + workflow + CODEOWNERS
authdiff check --locked .
```

Single CI recipe: [`aesa-consumer-gate.example.yml`](aesa-consumer-gate.example.yml).

### Secure Action pin (recommended)

Prefer an immutable commit SHA for the Action in high-assurance repos:

```yaml
- uses: roham-amd/agent-ecosystem-security-audit/.github/actions/aesa-gate@<commit-sha>
  with:
    trusted-policy: "true"
    authority-diff: "true"
    locked: "true"   # after AUTHORITY.lock exists
```

Minimum workflow permissions (example recipe):

```yaml
permissions:
  contents: read
  pull-requests: write   # sticky Authority Diff comment
  security-events: write # SARIF upload when enabled
```

---

## Tamper-resistant behavior

| Control | Behavior |
| --- | --- |
| Trusted policy | On PRs, load `.aesa.yml` from **base** ref when `trusted-policy: true` |
| First-time policy add | Adding `.aesa.yml` is allowed; weakening base policy on head fails |
| Lock drift | `locked: true` fails when observed authority ≠ `AUTHORITY.lock` |
| Suppressions | Retained in findings (`suppressed: true`), never deleted from evidence |
| Target policy default | Target `.aesa.yml` ignored unless `--policy` / `--trust-target-policy` |

---

## Hybrid responsibility

| Role | Responsibility | Final decision |
| --- | --- | --- |
| Deterministic tools | Inventory, rules, evidence, lock, SARIF | No |
| AI audit agent | Explanations / remediation proposals | No |
| Human operator | Scope, risk acceptance, lock approval | Yes |

Never ask an LLM to establish a fact a deterministic tool can establish.  
Never let an unsupported LLM interpretation become an enforced finding.  
Never let the agent edit or approve policy without a human.

---

## Interfaces

| Interface | Status |
| --- | --- |
| CLI (`doctor` / `vet` / `scan` / `lock`) | Primary product |
| GitHub Action (trusted policy) | Supported (composite) |
| AI agent skill | Supported (`skills/aesa-auditor`, thin) |
| Prompt-only kit | Archived methodology fallback |
| MCP server assistant | Deferred |
| Web workbench / marketplace | Deferred |

---

## Non-goals (for now)

- Marketplace “certified secure” badges
- SaaS multi-tenant evidence storage
- Bundled runtime detonation harness
- Numeric trust scores that hide coverage gaps
- Claiming detection accuracy without labeled sample counts
