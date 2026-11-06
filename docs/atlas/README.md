# Ecosystem Atlas

Public precision engine for AESA Guard (strategic review direction **#4**).

**Goal:** replace “external N = 0” AgentSecBench ceremony with a labeled sample of
real-world skills, MCP configs, and hook setups — then publish **per-rule precision**.

## Status

| Item | Status |
| --- | --- |
| Schema for scan + label records | draft (`PRECISION.md`) |
| Local benign + attack fixtures (`tests/atlas/`) | **seeded** (CI: `test_atlas_lite.py`) |
| Crawl harness (`authdiff atlas crawl --demo-seed`) | **shipped** (ledger under `docs/atlas/ledger/`; target N≥300) |
| Crawl of 300–1000 public repos | next (feed seed JSON) |
| Blind label of ~100 findings | next |
| Publish per-rule precision | next |
| AgentSecBench intake vault / outreach funnel | **frozen** (keep schema; stop expanding governance) |

## Workflow

1. Crawl → `aesa scan` → store findings + inventory digests.
2. Sample stratified by rule id and evidence_strength.
3. Blind-label: true positive / false positive / inconclusive.
4. Publish precision; kill or demote rules below ~70%; keep `NAME_MARKER` ≤ LOW.

## Responsible disclosure

Aggregate by default. Name individual repos only with coordinated disclosure.
Do not publish secret values from scanned configs.
