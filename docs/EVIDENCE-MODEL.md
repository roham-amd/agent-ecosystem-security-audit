# Evidence, capabilities, findings, and claims

AESA Guard’s intellectual core is an **evidence-first** model. This document is normative for how deterministic tooling and AI auditors must treat facts.

Related: [`SECURITY-RULES.md`](SECURITY-RULES.md), [`../prompts/03-report-contract.md`](../prompts/03-report-contract.md), [`../schemas/structured-claim.schema.json`](../schemas/structured-claim.schema.json).

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

Capability-first assessment is preferred over merely counting component types. See [`threat-scenarios.md`](threat-scenarios.md).

---

## Evidence record fields (Guard)

| Field | Purpose |
| --- | --- |
| `evidence_id` | Stable reference (`E-001`, `E-INV-C-001`, …) |
| `component_id` | Related component |
| `source_commit` | Exact audited revision when known |
| `file_path` | Exact source location |
| `line_start` / `line_end` | Reproducible location when available |
| `content_digest` | Integrity when computed |
| `evidence_class` | Class enum above |
| `collection_method` | `deterministic_rule`, `inventory_adapter`, human, … |
| `observed_at` | Collection timestamp |
| `verification_status` | Status enum |
| `limitations` | What this evidence cannot establish |
| `summary` | Short description |

### Freshness vs strength

- **Freshness:** Is evidence still applicable to the current component version?
- **Strength:** How strongly does it support the claim?

A hash proves digest match — not safety. Model agreement is not independent verification.

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

Full narrative structure: [`../prompts/01-core-prompt.md`](../prompts/01-core-prompt.md) Section 21. JSON contract: [`../prompts/03-report-contract.md`](../prompts/03-report-contract.md).
