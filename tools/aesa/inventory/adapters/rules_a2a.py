from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aesa.inventory.io import safe_read_text, select_files
from aesa.inventory.limits import CollectorLimits

_CARD_NAMES = {"agent-card.json", "agent_card.json"}


def discover_agent_cards(
    root: Path,
    *,
    files: list[Path],
    limits: CollectorLimits,
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for path in select_files(
        files,
        lambda p: p.name in _CARD_NAMES
        or (p.name == "agent-card.json" and ".well-known" in p.parts),
    ):
        raw = safe_read_text(path, root=root, limits=limits, events=events, adapter="a2a_agent_card")
        if raw is None:
            continue
        rel = path.relative_to(root).as_posix()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            events.append(
                {
                    "type": "parse_error",
                    "adapter": "a2a_agent_card",
                    "path": rel,
                    "message": str(exc),
                }
            )
            continue
        results.append(
            {
                "name": data.get("name") or path.parent.name,
                "type": "A2A Agent Card",
                "reference_kind": "LOCAL_CONFIGURATION_OR_INSTRUCTIONS",
                "repository_path": rel,
                "adapter": "a2a_agent_card",
                "adapter_maturity": "PARTIAL",
                "discovery_status": "IDENTIFIED",
                "declared_url": data.get("url"),
                "priority_hints": ["remote_agent_identity"] if data.get("url") else [],
            }
        )
    return results


def discover_instruction_rules(
    root: Path,
    *,
    files: list[Path],
    limits: CollectorLimits,
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    seen_dirs: set[str] = set()
    for path in select_files(
        files,
        lambda p: p.name in {"AGENTS.md", "CLAUDE.md"}
        or (".cursor" in p.parts and "rules" in p.parts),
    ):
        rel = path.relative_to(root).as_posix()
        if path.name in {"AGENTS.md", "CLAUDE.md"}:
            # Confirm readable under limits (content not required for identity)
            raw = safe_read_text(
                path, root=root, limits=limits, events=events, adapter="instruction_rules"
            )
            if raw is None:
                continue
            results.append(
                {
                    "name": path.name,
                    "type": "Rule / instruction file",
                    "reference_kind": "LOCAL_CONFIGURATION_OR_INSTRUCTIONS",
                    "repository_path": rel,
                    "adapter": "instruction_rules",
                    "adapter_maturity": "SUPPORTED",
                    "discovery_status": "IDENTIFIED",
                    "instruction_content_present": True,
                    "priority_hints": [],
                }
            )
            continue

        # Cursor rules: group by rules directory
        rules_dir = None
        parts = path.relative_to(root).parts
        for i, part in enumerate(parts):
            if part == "rules" and i > 0 and parts[i - 1] == ".cursor":
                rules_dir = "/".join(parts[: i + 1])
                break
        if not rules_dir or rules_dir in seen_dirs:
            continue
        seen_dirs.add(rules_dir)
        results.append(
            {
                "name": "cursor-rules",
                "type": "Rule pack",
                "reference_kind": "LOCAL_CONFIGURATION_OR_INSTRUCTIONS",
                "repository_path": rules_dir,
                "adapter": "instruction_rules",
                "adapter_maturity": "PARTIAL",
                "discovery_status": "IDENTIFIED",
                "priority_hints": [],
            }
        )
    return results
