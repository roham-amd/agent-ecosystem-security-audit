from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def discover_agent_cards(
    root: Path,
    *,
    limits,
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    names = ("agent-card.json", ".well-known/agent-card.json")
    for path in root.rglob("*"):
        if path.name not in names and path.name != "agent_card.json":
            continue
        if ".git" in path.parts or "node_modules" in path.parts:
            continue
        try:
            rel = path.relative_to(root)
            raw = path.read_text(encoding="utf-8")
            if len(raw.encode("utf-8")) > limits.max_file_bytes:
                events.append({"type": "parse_skipped_size", "path": str(rel)})
                continue
            data = json.loads(raw)
        except (OSError, json.JSONDecodeError) as exc:
            events.append(
                {
                    "type": "parse_error",
                    "adapter": "a2a_agent_card",
                    "path": str(path.relative_to(root)),
                    "message": str(exc),
                }
            )
            continue
        results.append(
            {
                "name": data.get("name") or path.parent.name,
                "type": "A2A Agent Card",
                "reference_kind": "LOCAL_CONFIGURATION_OR_INSTRUCTIONS",
                "repository_path": str(rel),
                "adapter": "a2a_agent_card",
                "adapter_maturity": "partial",
                "discovery_status": "IDENTIFIED",
                "declared_url": data.get("url"),
            }
        )
    return results


def discover_instruction_rules(
    root: Path,
    *,
    limits,
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    patterns = (
        "AGENTS.md",
        "CLAUDE.md",
        ".cursor/rules",
    )
    for path in root.rglob("*"):
        if ".git" in path.parts or "node_modules" in path.parts:
            continue
        rel = path.relative_to(root)
        if path.name in ("AGENTS.md", "CLAUDE.md"):
            results.append(
                {
                    "name": path.name,
                    "type": "Rule / instruction file",
                    "reference_kind": "LOCAL_CONFIGURATION_OR_INSTRUCTIONS",
                    "repository_path": str(rel),
                    "adapter": "instruction_rules",
                    "adapter_maturity": "supported",
                    "discovery_status": "IDENTIFIED",
                    "instruction_content_present": True,
                }
            )
        elif path.is_dir() and path.name == "rules" and ".cursor" in path.parts:
            results.append(
                {
                    "name": "cursor-rules",
                    "type": "Rule pack",
                    "reference_kind": "LOCAL_CONFIGURATION_OR_INSTRUCTIONS",
                    "repository_path": str(rel),
                    "adapter": "instruction_rules",
                    "adapter_maturity": "partial",
                    "discovery_status": "IDENTIFIED",
                }
            )
    return results
