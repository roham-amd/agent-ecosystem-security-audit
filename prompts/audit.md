# AI AGENT ECOSYSTEM SECURITY AUDIT — v1.0 (kit entry)

This procedure is split into a **kit** to reduce context size and load modules on demand.
Product tooling is **AESA Guard 3.1** (`aesa scan`); procedure version remains **1.0**.

**Start here:**

0. Prefer deterministic Guard scan first: `aesa scan <target>` — [`../docs/GUARD-SCAN.md`](../docs/GUARD-SCAN.md)
1. Operators: [`00-OPERATOR-GUIDE.md`](00-OPERATOR-GUIDE.md) · Docs map: [`../docs/DOCUMENTATION-INDEX.md`](../docs/DOCUMENTATION-INDEX.md)
2. Load guardrails: [`04-passive-guardrails.md`](04-passive-guardrails.md) (Section 1 for every worker)
3. Audit agent: [`../skills/aesa-auditor/SKILL.md`](../skills/aesa-auditor/SKILL.md) or [`01-core-prompt.md`](01-core-prompt.md) — fill Section 2 (`KIT_DIR`, `WORK_DIR`, …)
4. Deep audit: [`02-modules.md`](02-modules.md) + applicable [`modules/`](../modules/) (index: [`../modules/README.md`](../modules/README.md))
5. Claims + JSON: [`../docs/EVIDENCE-MODEL.md`](../docs/EVIDENCE-MODEL.md), [`03-report-contract.md`](03-report-contract.md), [`../schemas/`](../schemas/)

Full monolithic procedure: [`audit.full.md`](audit.full.md)
