from __future__ import annotations

from typing import Any

# Maturity of deterministic discovery for each ecosystem family.
ADAPTER_COVERAGE: list[dict[str, str]] = [
    {
        "family": "Skill",
        "adapter": "skill_md",
        "maturity": "SUPPORTED",
        "notes": "Discovers SKILL.md manifests; does not verify runtime behavior.",
    },
    {
        "family": "MCP",
        "adapter": "mcp_config",
        "maturity": "PARTIAL",
        "notes": "Client registration configs only; server source and auth require manual/agent review.",
    },
    {
        "family": "A2A",
        "adapter": "a2a_agent_card",
        "maturity": "PARTIAL",
        "notes": "Agent card JSON identity; message trust and delegation are MANUAL_ONLY.",
    },
    {
        "family": "Instruction rules",
        "adapter": "instruction_rules",
        "maturity": "SUPPORTED",
        "notes": "AGENTS.md, CLAUDE.md, and Cursor rules pack paths.",
    },
    {
        "family": "Hook",
        "adapter": "hooks",
        "maturity": "PARTIAL",
        "notes": "Common hooks.json / hooks/ layouts; host-specific formats may be missed.",
    },
    {
        "family": "Plugin",
        "adapter": "plugins",
        "maturity": "PARTIAL",
        "notes": "Manifest heuristics only; publisher and OAuth scopes are MANUAL_ONLY.",
    },
    {
        "family": "Subagent",
        "adapter": "subagents",
        "maturity": "PARTIAL",
        "notes": "agents/ and subagents/ definitions; inherited permissions need deep review.",
    },
    {
        "family": "Automation",
        "adapter": "automations",
        "maturity": "PARTIAL",
        "notes": "Workflow and automation manifests; effective credentials are NOT VERIFIED.",
    },
    {
        "family": "Host effective permissions",
        "adapter": None,
        "maturity": "MANUAL_ONLY",
        "notes": "Requires host configuration evidence outside repository files.",
    },
    {
        "family": "Runtime behavior",
        "adapter": None,
        "maturity": "UNSUPPORTED",
        "notes": "No runtime harness in passive mode.",
    },
    {
        "family": "Publisher / artifact provenance",
        "adapter": None,
        "maturity": "MANUAL_ONLY",
        "notes": "Digest helpers exist; full signature/SBOM verification is not shipped.",
    },
]


def summarize_coverage(components: list[dict[str, Any]]) -> dict[str, Any]:
    by_maturity: dict[str, int] = {
        "SUPPORTED": 0,
        "PARTIAL": 0,
        "MANUAL_ONLY": 0,
        "UNSUPPORTED": 0,
    }
    by_type: dict[str, int] = {}
    for comp in components:
        maturity = str(comp.get("adapter_maturity") or "PARTIAL").upper()
        if maturity not in by_maturity:
            by_maturity[maturity] = 0
        by_maturity[maturity] += 1
        ctype = str(comp.get("type") or "Unknown")
        by_type[ctype] = by_type.get(ctype, 0) + 1

    high_priority: list[dict[str, Any]] = []
    for comp in components:
        hints = comp.get("priority_hints") or []
        if hints:
            high_priority.append(
                {
                    "component_id": comp.get("component_id"),
                    "name": comp.get("name"),
                    "type": comp.get("type"),
                    "repository_path": comp.get("repository_path"),
                    "hints": hints,
                }
            )

    return {
        "adapter_matrix": ADAPTER_COVERAGE,
        "component_counts_by_type": by_type,
        "component_counts_by_maturity": by_maturity,
        "deterministically_discovered": by_maturity.get("SUPPORTED", 0)
        + by_maturity.get("PARTIAL", 0),
        "manual_review_families": [
            row["family"] for row in ADAPTER_COVERAGE if row["maturity"] in {"MANUAL_ONLY", "UNSUPPORTED"}
        ],
        "high_priority_review_areas": high_priority[:25],
        "not_verified": [
            "Runtime behavior",
            "Publisher identity",
            "Effective host permissions",
            "Credential isolation",
        ],
    }
