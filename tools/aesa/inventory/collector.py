from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aesa.inventory.adapters.host_components import (
    discover_automations,
    discover_plugins,
    discover_subagents,
)
from aesa.inventory.adapters.hooks import discover_hooks
from aesa.inventory.adapters.mcp import discover_mcp_configs
from aesa.inventory.adapters.rules_a2a import discover_agent_cards, discover_instruction_rules
from aesa.inventory.adapters.skills import discover_skills
from aesa.inventory.coverage import summarize_coverage
from aesa.inventory.io import iter_repo_files
from aesa.inventory.limits import CollectorLimits


@dataclass
class InventoryResult:
    repository_path: str
    collected_at_utc: str
    limits: dict[str, int]
    tree_summary: dict[str, Any]
    components: list[dict[str, Any]] = field(default_factory=list)
    parser_events: list[dict[str, Any]] = field(default_factory=list)
    coverage: dict[str, Any] = field(default_factory=dict)
    mode: str = "passive_read_only"


def collect_inventory(target: Path, *, limits: CollectorLimits | None = None) -> InventoryResult:
    limits = limits or CollectorLimits()
    target = target.resolve()
    if not target.exists():
        raise FileNotFoundError(target)

    events: list[dict[str, Any]] = []
    tree_summary, files = iter_repo_files(target, limits=limits, events=events)
    components: list[dict[str, Any]] = []
    seq = 1

    def next_id() -> str:
        nonlocal seq
        cid = f"C-{seq:03d}"
        seq += 1
        return cid

    discoveries = [
        discover_skills(target, files=files, limits=limits, events=events),
        discover_mcp_configs(target, files=files, limits=limits, events=events),
        discover_agent_cards(target, files=files, limits=limits, events=events),
        discover_instruction_rules(target, files=files, limits=limits, events=events),
        discover_hooks(target, files=files, limits=limits, events=events),
        discover_plugins(target, files=files, limits=limits, events=events),
        discover_subagents(target, files=files, limits=limits, events=events),
        discover_automations(target, files=files, limits=limits, events=events),
    ]
    for batch in discoveries:
        for item in batch:
            item["component_id"] = next_id()
            components.append(item)

    coverage = summarize_coverage(components)

    return InventoryResult(
        repository_path=str(target),
        collected_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        limits={
            "max_files": limits.max_files,
            "max_depth": limits.max_depth,
            "max_file_bytes": limits.max_file_bytes,
        },
        tree_summary=tree_summary,
        components=components,
        parser_events=events,
        coverage=coverage,
        mode="passive_read_only",
    )


def inventory_to_json(result: InventoryResult) -> dict[str, Any]:
    return {
        "aesa_inventory_version": "0.2.0",
        "mode": result.mode,
        "repository_path": result.repository_path,
        "collected_at_utc": result.collected_at_utc,
        "limits": result.limits,
        "tree_summary": result.tree_summary,
        "population_defined": True,
        "coverage": result.coverage,
        "components": result.components,
        "parser_events": result.parser_events,
        "notes": [
            "Passive inventory only — does not execute target code or contact endpoints.",
            "Deterministic discovery coverage is partial; see coverage.adapter_matrix.",
            "Inventory is not a security clearance or production approval.",
        ],
    }
