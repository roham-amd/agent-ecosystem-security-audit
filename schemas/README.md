# AESA JSON schemas

Machine-readable contracts for AESA Guard artifacts and audit engagements.

Canonical **audit report** source of truth:

- Edit: [`../canonical/schemas/audit-report.schema.json`](../canonical/schemas/audit-report.schema.json)
- Publish aliases: `aesa build schemas` → this directory

Validate instances:

```bash
aesa validate report path/to/summary.json
aesa validate graph path/to/ecosystem-graph.json
aesa validate claim path/to/claim.json
```

---

## Schema catalog

| File | Version field | Purpose |
| --- | --- | --- |
| [`audit-report.schema.json`](audit-report.schema.json) | `audit_version` **1.0** | Narrative engagement summary JSON (findings, coverage, decisions) |
| [`AI_Agent_Ecosystem_Security_Audit_v1.schema.json`](AI_Agent_Ecosystem_Security_Audit_v1.schema.json) | same | Legacy filename alias (byte-identical after build) |
| [`ecosystem-graph.schema.json`](ecosystem-graph.schema.json) | `graph_version` **1.0** | Nodes/edges/attack_paths seed |
| [`audit-manifest.schema.json`](audit-manifest.schema.json) | `manifest_version` **1.0** | Engagement scope / acquisition metadata |
| [`audit-diff.schema.json`](audit-diff.schema.json) | `diff_version` **1.0** | Structural report/graph diffs |
| [`evidence-digest-manifest.schema.json`](evidence-digest-manifest.schema.json) | `manifest_version` **1.0** | Passive digest inventory |
| [`runtime-test-record.schema.json`](runtime-test-record.schema.json) | `record_version` **1.0** | Authorized runtime test records (not passive default) |
| [`structured-claim.schema.json`](structured-claim.schema.json) | (object) | Intermediate AI auditor claims for `aesa validate claim` |

---

## Guard scan JSON (not separate JSON Schema files)

`aesa scan` writes additional documents validated by tooling conventions rather than the audit-report schema:

| Artifact | Documented in |
| --- | --- |
| `findings.json` | [`../docs/GUARD-SCAN.md`](../docs/GUARD-SCAN.md), [`../docs/EVIDENCE-MODEL.md`](../docs/EVIDENCE-MODEL.md) |
| `inventory.json` | Product spec adapter matrix; collector `aesa_inventory_version` |
| `baseline.json` / `risk-delta.json` | [`../docs/GUARD-SCAN.md`](../docs/GUARD-SCAN.md) |
| `findings.sarif.json` | SARIF 2.1.0 via `aesa.export.sarif` |

---

## Semantic validation

JSON Schema compliance is necessary but not sufficient. `aesa validate report|graph` also runs semantic checks (orphan evidence, duplicate ids, dangling graph refs). See [`../docs/archive/architecture/ADR-002-semantic-validation.md`](../docs/archive/architecture/ADR-002-semantic-validation.md).

---

## Examples

| Example | Schema |
| --- | --- |
| [`../examples/sample-audit-summary.json`](../examples/sample-audit-summary.json) | audit-report |
| [`../examples/sample-component-inventory.json`](../examples/sample-component-inventory.json) | inventory-shaped (illustrative) |
| [`../examples/sample-runtime-test-record.json`](../examples/sample-runtime-test-record.json) | runtime-test-record |
| [`../examples/sample-audit-manifest.yaml`](../examples/sample-audit-manifest.yaml) | audit-manifest (YAML illustration) |
| [`../examples/sample-audit-context.yaml`](../examples/sample-audit-context.yaml) | operator context illustration |
