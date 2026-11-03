# AESA Guard deterministic security rules

Rules live in `tools/aesa/security/rules.py` and are applied by `aesa scan`.

**Version:** rule pack **1.1** (embedded in tooling **0.4.1**).

**Discipline:** rules emit findings with confidence `OBSERVED` or `POTENTIAL`. They never claim confirmed runtime exploitation. Every finding references evidence and lists missing controls.

**Finding classes (required distinction):**

| Class | Meaning | Typical severity |
| --- | --- | --- |
| `CAPABILITY` | What the component can potentially do | INFORMATIONAL / LOW |
| `EXPOSURE` | How reachable that capability is | LOW / MEDIUM |
| `SECURITY_FINDING` | Evidenced concern given exposure + missing controls | MEDIUM / HIGH / CRITICAL |

`--fail-on high|any` gates on `SECURITY_FINDING` and `EXPOSURE` only — pure capability observations do not fail CI.

---

## How rules fire

1. Inventory adapters attach `priority_hints` and typed component records.
2. The scan engine enriches components with `content_digest` and `fingerprint`.
3. `apply_all_rules(components, ctx=…)` runs each `RuleSpec` with commit/digest provenance.
4. Matching rules append `Evidence` + `Finding` objects (with `finding_class`).
5. Results appear in `findings.json`, the terminal report, and SARIF.

Absent a matching hint/type, a rule does nothing for that component.

---

## Rule catalog

| Rule id | Title | Class (default) | Typical severity | Triggers (summary) |
| --- | --- | --- | --- |
| `AESA-RULE-001` | Skill references executable scripts | CAPABILITY → EXPOSURE/SECURITY when escalated | INFO / MEDIUM / HIGH | Skill script hints; HIGH only with bundled scripts + secrets handling |
| `AESA-RULE-002` | MCP local command transport | CAPABILITY; SECURITY_FINDING with env or broad args | INFO / HIGH / CRITICAL | Local `command`; escalate on `inherits_or_sets_environment` or `broad_or_relative_path_args` |
| `AESA-RULE-003` | MCP remote endpoint | EXPOSURE | MEDIUM | MCP registration with `url` / `remote_endpoint` |
| `AESA-RULE-004` | Hook execution boundary | CAPABILITY or SECURITY_FINDING | INFO / MEDIUM | Hook execution / pre-tool lifecycle hints |
| `AESA-RULE-005` | Skill external URLs | EXPOSURE | LOW | Skill hint: `external_url_reference` |
| `AESA-RULE-006` | Skill secrets handling | SECURITY_FINDING | MEDIUM | Skill secrets / identity workflow hints |
| `AESA-RULE-007` | Unattended automation | CAPABILITY (SECURITY if secret hints) | INFO / MEDIUM | Type `Automation`, `CI Workflow`, or `Workflow` |
| `AESA-RULE-008` | Subagent delegation | CAPABILITY | INFORMATIONAL | Type `Subagent` |
| `AESA-RULE-009` | Example MCP config | EXPOSURE | LOW | MCP hint: `example_or_template_config` |
| `AESA-RULE-010` | Prompt-injection oriented surface | CAPABILITY | LOW | Name/path markers (weak indicator) |

---

## Per-rule detail

### AESA-RULE-001 — Skill references executable scripts

- **Default class:** CAPABILITY (execution capability ≠ vulnerability)
- **Escalation:** bundled scripts directory → EXPOSURE/MEDIUM; plus secrets handling → SECURITY_FINDING/HIGH
- **Recommended action:** Verify script env inheritance and whether execution needs independent approval

### AESA-RULE-002 — MCP server launched via local command

- **Default class:** CAPABILITY / INFORMATIONAL — a local process is not automatically malicious
- **Escalation:** `broad_or_relative_path_args` → SECURITY_FINDING/HIGH; env inheritance → CRITICAL
- **Recommended action:** Pin/verify artifacts; restrict env; require approval for high-impact tools

### AESA-RULE-003 — MCP server uses remote endpoint

- **Class:** EXPOSURE / MEDIUM — a remote URL is not automatically unsafe
- **Recommended action:** Verify TLS/identity, OAuth scopes, credential forwarding

### AESA-RULE-004 — Hook can intercept or execute around tool use

- **Class:** CAPABILITY unless pre-tool lifecycle → SECURITY_FINDING/MEDIUM
- **Recommended action:** Confirm post-approval argument integrity and hook execution identity

### AESA-RULE-005 — Skill references external URLs

- **Class:** EXPOSURE / LOW — a URL is not proof of malicious content
- **Recommended action:** Pin/vendor remote references; treat remote content as untrusted

### AESA-RULE-006 — Skill references secrets or identity workflows

- **Class:** SECURITY_FINDING / MEDIUM — requires context and reachability review
- **Recommended action:** Prefer brokers; ensure skills cannot print/forward live secrets

### AESA-RULE-007 — Unattended automation or CI workflow

- **Default class:** CAPABILITY / INFORMATIONAL — legitimate automation can be secure
- **Escalation:** secret/env hints → SECURITY_FINDING/MEDIUM
- **Recommended action:** Review triggers, secrets, permissions, cancellation

### AESA-RULE-008 — Subagent may inherit delegated authority

- **Class:** CAPABILITY / INFORMATIONAL — delegation alone is not a defect
- **Recommended action:** Verify privilege reduction, message auth, memory isolation

### AESA-RULE-009 — Example MCP config may be mistaken for production

- **Class:** EXPOSURE / LOW
- **Recommended action:** Keep examples off the host MCP search path

### AESA-RULE-010 — Potential prompt-injection oriented instruction surface

- **Class:** CAPABILITY / LOW — naming is a weak indicator
- **Recommended action:** Review full instruction text; do not auto-activate in privileged hosts

---

## Finding object fields (emitted by rules)

| Field | Purpose |
| --- | --- |
| `finding_id` | Stable within a scan (`F-001`, …) |
| `rule_id` | Catalog id above |
| `finding_class` | `CAPABILITY` / `EXPOSURE` / `SECURITY_FINDING` |
| `title` / `description` | Human-readable summary |
| `severity` | CRITICAL / HIGH / MEDIUM / LOW / INFORMATIONAL |
| `confidence` | OBSERVED / POTENTIAL (not CONFIRMED from rules alone) |
| `component_ids` / `evidence_ids` | Traceability |
| `capabilities` | Related capability kinds |
| `attacker_control` → `impact` | Exploitability reasoning chain |
| `missing_controls` | Evidence/control gaps |
| `recommended_action` | Next operator step |

Evidence records should include `file_path`, `line_start`/`line_end` when locatable, `content_digest`, and `source_commit` when known.

---

## Extending the rule pack

1. Add a function in `tools/aesa/security/rules.py`.
2. Register a `RuleSpec` in `RULES` (bump rule `version`).
3. Require positive, negative, and ambiguous fixtures before shipping HIGH/CRITICAL defaults.
4. Document it in this file and bump CHANGELOG.
5. Add AgentSecBench `expect_rule_ids` / `forbid_rule_ids` where applicable.
6. Prefer: observation → capability → exposure conditions → missing control → security finding.

Do not invent a single numeric “trust score.” Keep severity, confidence, exploitability, exposure, finding class, and coverage separate ([`EVIDENCE-MODEL.md`](EVIDENCE-MODEL.md)).
