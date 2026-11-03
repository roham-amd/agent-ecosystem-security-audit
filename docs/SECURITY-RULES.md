# AESA Guard deterministic security rules

Rules live in `tools/aesa/security/rules.py` and are applied by `aesa scan`.

**Version:** rule pack embedded in tooling **0.4.0** (each rule carries `version: "1.0"`).

**Discipline:** rules emit findings with confidence `OBSERVED` or `POTENTIAL`. They never claim confirmed runtime exploitation. Every finding references evidence and lists missing controls.

---

## How rules fire

1. Inventory adapters attach `priority_hints` and typed component records.
2. `apply_all_rules(components)` runs each `RuleSpec` against every component.
3. Matching rules append `Evidence` + `Finding` objects.
4. Results appear in `findings.json`, the terminal report, and SARIF.

Absent a matching hint/type, a rule does nothing for that component.

---

## Rule catalog

| Rule id | Title | Typical severity | Triggers (summary) |
| --- | --- | --- | --- |
| `AESA-RULE-001` | Skill references executable scripts | HIGH | Skill hints: `bundled_scripts_directory`, `script_reference`, or `possible_code_execution_reference` |
| `AESA-RULE-002` | MCP local command transport | HIGH (CRITICAL if env inheritance) | MCP registration with `command` / `local_command_transport` |
| `AESA-RULE-003` | MCP remote endpoint | HIGH | MCP registration with `url` / `remote_endpoint` |
| `AESA-RULE-004` | Hook execution boundary | HIGH | Hook hints: `possible_execution_boundary` or `pre_execution_lifecycle` |
| `AESA-RULE-005` | Skill external URLs | MEDIUM | Skill hint: `external_url_reference` |
| `AESA-RULE-006` | Skill secrets handling | HIGH | Skill hints: `secrets_or_credential_handling` or `identity_or_auth_workflow` |
| `AESA-RULE-007` | Unattended automation | MEDIUM | Type `Automation`, `CI Workflow`, or `Workflow` |
| `AESA-RULE-008` | Subagent delegation | MEDIUM | Type `Subagent` |
| `AESA-RULE-009` | Example MCP config | LOW | MCP hint: `example_or_template_config` |
| `AESA-RULE-010` | Prompt-injection oriented surface | HIGH | Skill/Rule pack name or path contains injection-oriented markers |

---

## Per-rule detail

### AESA-RULE-001 — Skill references executable scripts

- **Attacker control:** Malicious or compromised skill instructions/scripts
- **Trust boundary:** Agent instruction surface → host execution
- **Impact:** Potential local command execution under the host agent identity
- **Recommended action:** Verify script env inheritance and whether execution needs independent approval

### AESA-RULE-002 — MCP server launched via local command

- **Attacker control:** Compromised MCP binary/package or poisoned tool metadata
- **Trust boundary:** Host agent → MCP child process
- **Impact:** Tool calls execute under the MCP process identity
- **Escalation:** Severity CRITICAL when `inherits_or_sets_environment` is also present
- **Recommended action:** Pin/verify artifacts; restrict env; require approval for high-impact tools

### AESA-RULE-003 — MCP server uses remote endpoint

- **Attacker control:** Compromised remote endpoint or MITM without transport identity
- **Trust boundary:** Host agent → remote network service
- **Impact:** Potential exfiltration or tool abuse via remote MCP
- **Recommended action:** Verify TLS/identity, OAuth scopes, credential forwarding

### AESA-RULE-004 — Hook can intercept or execute around tool use

- **Attacker control:** Malicious hook definition or poisoned hook input
- **Trust boundary:** User approval → hook mutation → tool execution
- **Impact:** Approved actions may be altered; privileged commands may run unexpectedly
- **Recommended action:** Confirm post-approval argument integrity and hook execution identity

### AESA-RULE-005 — Skill references external URLs

- **Attacker control:** Compromised remote resource referenced by the skill
- **Trust boundary:** Reviewed skill → unreviewed remote content
- **Impact:** Instruction injection or data exfiltration guidance
- **Recommended action:** Pin/vendor remote references; treat remote content as untrusted

### AESA-RULE-006 — Skill references secrets or identity workflows

- **Attacker control:** Prompt injection causing credential-handling steps
- **Trust boundary:** Agent context → credential stores / identity tooling
- **Impact:** Potential credential disclosure or misuse
- **Recommended action:** Prefer brokers; ensure skills cannot print/forward live secrets

### AESA-RULE-007 — Unattended automation or CI workflow

- **Attacker control:** Malicious trigger payload or compromised workflow definition
- **Trust boundary:** Trigger → privileged unattended execution
- **Impact:** Actions may run without interactive human approval
- **Recommended action:** Review triggers, secrets, permissions, cancellation

### AESA-RULE-008 — Subagent may inherit delegated authority

- **Attacker control:** Compromised parent agent or poisoned delegated task
- **Trust boundary:** Parent agent → subagent
- **Impact:** Excessive authority or cross-tenant exposure via delegation
- **Recommended action:** Verify privilege reduction, message auth, memory isolation

### AESA-RULE-009 — Example MCP config may be mistaken for production

- **Attacker control:** Accidental promotion of example config into a live host
- **Trust boundary:** Documentation/example → live agent configuration
- **Impact:** Unexpected tool surface if examples are installed
- **Recommended action:** Keep examples off the host MCP search path

### AESA-RULE-010 — Potential prompt-injection oriented instruction surface

- **Attacker control:** Instruction content in the component itself
- **Trust boundary:** Untrusted instructions → privileged agent tools
- **Impact:** Agent may follow injected instructions into privileged actions
- **Markers:** path/name contains tokens such as `injection`, `exfil`, `ignore previous`, `jailbreak`
- **Recommended action:** Review full instruction text; do not auto-activate in privileged hosts

---

## Finding object fields (emitted by rules)

| Field | Purpose |
| --- | --- |
| `finding_id` | Stable within a scan (`F-001`, …) |
| `rule_id` | Catalog id above |
| `title` / `description` | Human-readable summary |
| `severity` | CRITICAL / HIGH / MEDIUM / LOW / INFORMATIONAL |
| `confidence` | OBSERVED / POTENTIAL (not CONFIRMED from rules alone) |
| `component_ids` / `evidence_ids` | Traceability |
| `capabilities` | Related capability kinds |
| `attacker_control` → `impact` | Exploitability reasoning chain |
| `missing_controls` | Evidence/control gaps |
| `recommended_action` | Next operator step |

---

## Extending the rule pack

1. Add a function in `tools/aesa/security/rules.py`.
2. Register a `RuleSpec` in `RULES`.
3. Document it in this file and bump CHANGELOG.
4. Add AgentSecBench `expect_rule_ids` / `forbid_rule_ids` where applicable.
5. Keep confidence honest — static observations are not runtime confirmation.

Do not invent a single numeric “trust score.” Keep severity, confidence, exploitability, exposure, and coverage separate ([`EVIDENCE-MODEL.md`](EVIDENCE-MODEL.md)).
