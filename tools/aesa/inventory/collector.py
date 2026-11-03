from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aesa.inventory.limits import CollectorLimits
from aesa.inventory.adapters.mcp import discover_mcp_configs
from aesa.inventory.adapters.rules_a2a import discover_agent_cards, discover_instruction_rules
from aesa.inventory.adapters.skills import discover_skills



@dataclass
class InventoryResult:
    repository_path: str
    collected_at_utc: str
    limits: dict[str, int]
    tree_summary: dict[str, Any]
    components: list[dict[str, Any]] = field(default_factory=list)
    parser_events: list[dict[str, Any]] = field(default_factory=list)
    mode: str = "passive_read_only"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _walk_tree(root: Path, limits: CollectorLimits) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []
    file_count = 0
    symlink_count = 0
    skipped: list[str] = []

    def on_error(err: OSError) -> None:
        events.append({"type": "walk_error", "message": str(err)})

    for dirpath, dirnames, filenames in os.walk(root, onerror=on_error, followlinks=False):
        rel_dir = Path(dirpath).relative_to(root)
        depth = len(rel_dir.parts)
        if depth >= limits.max_depth:
            dirnames[:] = []
            events.append({"type": "depth_limit", "path": str(rel_dir)})
            continue
        dirnames[:] = [
            d
            for d in dirnames
            if d not in {".git", "node_modules", ".venv", "venv", "__pycache__"}
        ]
        for name in filenames:
            if file_count >= limits.max_files:
                events.append({"type": "file_limit_reached", "path": str(rel_dir)})
                return (
                    {
                        "file_count": file_count,
                        "symlink_count": symlink_count,
                        "truncated": True,
                        "skipped_reasons": skipped,
                    },
                    events,
                )
            p = Path(dirpath) / name
            file_count += 1
            if p.is_symlink():
                symlink_count += 1
                events.append({"type": "symlink_recorded_not_followed", "path": str(p.relative_to(root))})
            try:
                if p.is_file() and p.stat().st_size > limits.max_file_bytes:
                    skipped.append(str(p.relative_to(root)))
            except OSError as exc:
                events.append({"type": "stat_error", "path": str(p.relative_to(root)), "message": str(exc)})

    return (
        {
            "file_count": file_count,
            "symlink_count": symlink_count,
            "truncated": False,
            "skipped_reasons": skipped,
        },
        events,
    )


def collect_inventory(target: Path, *, limits: CollectorLimits | None = None) -> InventoryResult:
    limits = limits or CollectorLimits()
    target = target.resolve()
    if not target.exists():
        raise FileNotFoundError(target)

    tree_summary, events = _walk_tree(target, limits)
    components: list[dict[str, Any]] = []
    seq = 1

    def next_id() -> str:
        nonlocal seq
        cid = f"C-{seq:03d}"
        seq += 1
        return cid

    for skill in discover_skills(target, limits=limits, events=events):
        skill["component_id"] = next_id()
        components.append(skill)

    for mcp in discover_mcp_configs(target, limits=limits, events=events):
        mcp["component_id"] = next_id()
        components.append(mcp)

    for card in discover_agent_cards(target, limits=limits, events=events):
        card["component_id"] = next_id()
        components.append(card)

    for rule in discover_instruction_rules(target, limits=limits, events=events):
        rule["component_id"] = next_id()
        components.append(rule)

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
        mode="passive_read_only",
    )


def inventory_to_json(result: InventoryResult) -> dict[str, Any]:
    return {
        "aesa_inventory_version": "0.1.0",
        "mode": result.mode,
        "repository_path": result.repository_path,
        "collected_at_utc": result.collected_at_utc,
        "limits": result.limits,
        "tree_summary": result.tree_summary,
        "population_defined": True,
        "components": result.components,
        "parser_events": result.parser_events,
        "notes": [
            "Passive inventory only — does not execute target code or contact endpoints.",
            "Parser maturity and unsupported formats are recorded in parser_events.",
        ],
    }
