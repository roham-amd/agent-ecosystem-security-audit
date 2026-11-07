# Evidence, capabilities, findings, and claims

authdiff’s intellectual core is an **evidence-first** model. This document is normative for how deterministic tooling and AI auditors must treat facts.

Related: [`PRODUCT.md`](PRODUCT.md), [`AUTHORITY-LOCK.md`](AUTHORITY-LOCK.md), [`SECURITY-RULES.md`](SECURITY-RULES.md), [`../archive/methodology/prompts/03-report-contract.md`](../archive/methodology/prompts/03-report-contract.md), [`../schemas/structured-claim.schema.json`](../schemas/structured-claim.schema.json).

---

## Five core objects

| Object | Meaning | Primary producer |
| --- | --- | --- |
| **Component** | What exists in the ecosystem | Inventory adapters |
| **Capability** | What it appears able to do | Capability extractor + modules |
| **Evidence** | What establishes a fact | Collectors, rules, humans, runtime (if authorized) |
| **Finding** | Security concern tied to evidence | Rules + AI/human review |
| **Relationship** | How components/capabilities connect | Graph seed + deep review |

The audit **report** is a serialization of these objects — not the source of truth.

---

## Capability vs exposure vs finding

Do **not** treat detection of a security-relevant capability as a vulnerability.

| Concept | Question | Example |
| --- | --- | --- |
| **Capability** | What can it potentially do? | MCP server launches a local command |
| **Exposure** | How reachable is that capability, and under which identity? | Remote endpoint; broad filesystem args |
| **Security finding** | Is there an evidenced violation of a security property? | Local MCP inherits unrestricted production credentials |

Capability origins (Guard 3.1.1+):

| Origin | Meaning |
| --- | --- |
| `DECLARED` | Explicitly present in configuration / instructions |
| `POTENTIAL` | Hint-derived; not independently verified |
| `TYPE_DEFAULT` | Assumed from component type alone — never “effective” |
| `EFFECTIVE` | Host/integration evidence of actual authority |
| `VERIFIED` | Independently verified (authorized runtime test) |

Finding classes emitted by rules: `CAPABILITY`, `EXPOSURE`, `SECURITY_FINDING`.

Evidence strength (findings contract **1.2** / Guard **3.5**):

| Strength | Meaning | Typical rules |
| --- | --- | --- |
| `LITERAL_CONFIG` | Value taken from config/instruction bytes | Unpinned launcher, HTTP URL, literal env secret |
| `INFERRED_HINT` | Adapter hint / multi-signal inference | Most RULE-001…009 paths |
| `NAME_MARKER` | Path/name only — weak triage signal | RULE-010 |

Findings may also include `verify_in_60s` (reproduction hint) and `fix_snippet`.

---

## Evidence classes

Never upgrade one class into another without new evidence.

| Class | Establishes | Does not establish |
| --- | --- | --- |
| `SOURCE_STATIC` | What is written in repository files | Runtime behavior, effective host policy |
| `ARTIFACT` | Bytes of a built/packaged artifact | That source equals the installed binary |
| `PROVENANCE` | Origin / signature / publisher claims (when evidenced) | Safety of behavior |
| `HOST_CONFIGURATION` | Declared host settings | That settings are enforced at runtime |
| `RUNTIME` | Observed execution in an authorized test | Behavior in other environments |
| `EXTERNAL_INTELLIGENCE` | Third-party advisories / intel | Applicability without local evidence |
| `USER_ASSERTION` | Operator-stated facts | Independent verification |

---

## Verification / claim status

| Status | Meaning |
| --- | --- |
| `OBSERVED` | Directly seen in evidence (e.g. config line present) |
| `CONFIRMED` | Independently verified; **requires evidence_ids** |
| `POTENTIAL` | Plausible path; missing links remain |
| `NOT VERIFIED` | Applicable but unevidenced |
| `NOT ASSESSED` | Out of scope for this engagement |
| `NOT APPLICABLE` | Not relevant (with reason) |

Guard rules emit `OBSERVED` or `POTENTIAL` only. AI auditors must not promote to `CONFIRMED` without cited evidence (`aesa validate claim` enforces non-empty `evidence_ids` for `CONFIRMED`).

---

## Capability kinds

Extracted by `tools/aesa/security/capabilities.py` and refined during deep review:

| Kind | Question |
| --- | --- |
| `read_files` | Can it read files? |
| `write_files` | Can it write files? |
| `execute_commands` | Can it execute commands? |
| `access_secrets` | Can it access secrets? |
| `access_network` | Can it reach the network? |
| `modify_agent_instructions` | Can it change agent instructions? |
| `invoke_tools` | Can it invoke other tools? |
| `delegate_tasks` | Can it delegate? |
| `modify_approvals` | Can it alter approval decisions? |
| `access_persistent_memory` | Can it access persistent memory? |
| `unattended_operation` | Can it run without a human present? |

Capability-first assessment is preferred over merely counting component types. See [`archive/threat-scenarios.md`](archive/threat-scenarios.md).

---

## Evidence record fields (chain of custody)

| Field | Purpose |
| --- | --- |
| `evidence_id` | Stable reference (`E-001`, `E-INV-C-001`, …) |
| `component_id` | Related component identity |
| `component_version` / source identity | Exact component version or source identity when known |
| `source_commit` | Exact audited revision when known |
| `artifact_digest` | Artifact digest when scanning a built package |
| `file_path` | Exact source location |
| `line_start` / `line_end` | Reproducible location when available |
| `content_digest` | Integrity of the observed bytes |
| `parser` / `adapter_version` | Which parser produced the observation |
| `rule_version` | Rule pack / rule id version when rule-derived |
| `evidence_class` | Class enum above |
| `collection_method` | `deterministic_rule`, `inventory_adapter`, human, … |
| `observed_at` | Collection timestamp |
| `verification_status` | Status enum |
| `derivation` | `directly_observed` \| `inferred` \| `user_supplied` |
| `limitations` | What this evidence cannot establish |
| `summary` | Short description |

Producers must populate `content_digest` and `source_commit` whenever the source
file and git commit are available, and `line_start`/`line_end` when a
configuration needle can be located. Findings reference evidence objects; AI
claims must not invent evidence by restating observations.

### Reproducibility question

A reviewer should be able to answer:

> Can I reproduce the same observation from the same component version, using
> the same parser and rule set?

`AUTHORITY.lock` must retain enough identity to distinguish a changed component
from a representation-only change ([`AUTHORITY-LOCK.md`](AUTHORITY-LOCK.md)).

### Freshness vs strength

- **Freshness:** Is evidence still applicable to the current component version?
- **Strength:** How strongly does it support the claim?

A hash proves digest match — not safety. Model agreement is not independent verification.

### False-confidence controls

- Keep **severity** and **confidence** separate.
- Do not gate critical CI fails on `NAME_MARKER` alone.
- Abstain: unparseable / oversized / unsupported → explicit gap, never silent clean.
- Suppressions remain visible in findings (`suppressed: true`) with justification.
- Untrusted PR policy is never auto-trusted (`trusted-policy` loads base ref).
- Clean result ≠ safe component; reports must state what was not tested.

---

## Finding dimensions (keep separate)

| Dimension | Meaning |
| --- | --- |
| Severity | Potential impact |
| Confidence | Strength of evidence / status |
| Exploitability | How realistically reachable |
| Exposure | How accessible the component is |
| Coverage | How much applicable surface was examined |
| Verification | Whether independently established |

Do **not** collapse these into one invented trust score.

A clean scan with 30% coverage is not equivalent to a clean assessment with complete applicable coverage. Missing evidence is never evidence of safety.

---

## Exploitability chain

Every serious finding should establish:

```text
Attacker control
      ↓
Entry point
      ↓
Trust boundary crossed
      ↓
Available capability
      ↓
Missing or ineffective control
      ↓
Security impact
```

If the chain cannot be established, report `POTENTIAL` or an evidence gap — not `CONFIRMED`.

---

## Structured claims (AI auditors)

Before writing the full narrative report, emit intermediate claims:

```json
{
  "claim": "Component can execute local shell commands",
  "status": "OBSERVED",
  "evidence_ids": ["E-001", "E-002"],
  "impact": "Potential local command execution",
  "missing_evidence": [
    "Host execution identity",
    "Effective approval enforcement"
  ],
  "component_ids": ["C-001"]
}
```

Validate:

```bash
aesa validate claim claim.json
```

Schema: [`../schemas/structured-claim.schema.json`](../schemas/structured-claim.schema.json).

---

## Finding lifecycle (engagements)

```text
NEW → TRIAGED → INVESTIGATING
        → CONFIRMED | REJECTED | INSUFFICIENT EVIDENCE
        → REMEDIATED → REVALIDATED
```

Preserve rejected findings and reasons. Revalidate after changes. Prefer baselines + `aesa diff risk` for recurring work ([`GUARD-SCAN.md`](GUARD-SCAN.md)).

---

## Report audiences

| Audience | Needs |
| --- | --- |
| Executive | Overall situation, top risks, deployment readiness, required gates |
| Developer | Exact file, what is wrong, how to fix, how to verify |
| Security reviewer | Evidence, attack path, verified vs inferred, residual risk |

Full narrative structure: [`../archive/methodology/prompts/01-core-prompt.md`](../archive/methodology/prompts/01-core-prompt.md) Section 21. JSON contract: [`../archive/methodology/prompts/03-report-contract.md`](../archive/methodology/prompts/03-report-contract.md).
