from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aesa.inventory.io import safe_read_text, select_files
from aesa.inventory.limits import CollectorLimits


def _is_mcp_config(path: Path, root: Path) -> bool:
    rel = path.relative_to(root).as_posix()
    return rel in {".cursor/mcp.json", ".vscode/mcp.json", "mcp.json"} or path.name == "mcp.json"


def discover_mcp_configs(
    root: Path,
    *,
    files: list[Path],
    limits: CollectorLimits,
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for path in select_files(files, lambda p: _is_mcp_config(p, root)):
        key = path.resolve()
        if key in seen:
            continue
        seen.add(key)
        raw = safe_read_text(path, root=root, limits=limits, events=events, adapter="mcp_config")
        if raw is None:
            continue
        rel = path.relative_to(root).as_posix()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            events.append(
                {
                    "type": "parse_error",
                    "adapter": "mcp_config",
                    "path": rel,
                    "message": str(exc),
                }
            )
            continue

        servers = data.get("mcpServers") or data.get("servers") or {}
        if not isinstance(servers, dict):
            events.append({"type": "unsupported_shape", "adapter": "mcp_config", "path": rel})
            continue

        for name, cfg in servers.items():
            if not isinstance(cfg, dict):
                continue
            hints: list[str] = []
            if cfg.get("command"):
                hints.append("local_command_transport")
            if cfg.get("env") or cfg.get("environment"):
                hints.append("inherits_or_sets_environment")
            if cfg.get("url"):
                hints.append("remote_endpoint")
            results.append(
                {
                    "name": name,
                    "type": "MCP Server Registration",
                    "reference_kind": "LOCAL_CONFIGURATION_OR_INSTRUCTIONS",
                    "repository_path": rel,
                    "adapter": "mcp_config",
                    "adapter_maturity": "PARTIAL",
                    "discovery_status": "IDENTIFIED",
                    "declared_transport": cfg.get("transport") or cfg.get("type"),
                    "command": cfg.get("command"),
                    "url": cfg.get("url"),
                    "priority_hints": hints,
                    "evidence_digest_sha256": None,
                }
            )
    return results
