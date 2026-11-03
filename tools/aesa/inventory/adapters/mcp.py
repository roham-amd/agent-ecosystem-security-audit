from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aesa.inventory.limits import CollectorLimits


def discover_mcp_configs(
    root: Path,
    *,
    limits: CollectorLimits,
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    patterns = [
        ".cursor/mcp.json",
        ".vscode/mcp.json",
        "mcp.json",
    ]
    seen: set[Path] = set()
    for rel in patterns:
        path = root / rel
        if not path.is_file() or path in seen:
            continue
        seen.add(path)
        try:
            raw = path.read_text(encoding="utf-8")
            if len(raw.encode("utf-8")) > limits.max_file_bytes:
                events.append({"type": "parse_skipped_size", "path": str(path.relative_to(root))})
                continue
            data = json.loads(raw)
        except (OSError, json.JSONDecodeError) as exc:
            events.append(
                {
                    "type": "parse_error",
                    "adapter": "mcp_config",
                    "path": str(path.relative_to(root)),
                    "message": str(exc),
                }
            )
            continue

        servers = data.get("mcpServers") or data.get("servers") or {}
        if isinstance(servers, dict):
            for name, cfg in servers.items():
                if not isinstance(cfg, dict):
                    continue
                results.append(
                    {
                        "name": name,
                        "type": "MCP Server Registration",
                        "reference_kind": "LOCAL_CONFIGURATION_OR_INSTRUCTIONS",
                        "repository_path": str(path.relative_to(root)),
                        "adapter": "mcp_config",
                        "adapter_maturity": "partial",
                        "discovery_status": "IDENTIFIED",
                        "declared_transport": cfg.get("transport") or cfg.get("type"),
                        "command": cfg.get("command"),
                        "url": cfg.get("url"),
                        "evidence_digest_sha256": None,
                    }
                )
        else:
            events.append(
                {
                    "type": "unsupported_shape",
                    "adapter": "mcp_config",
                    "path": str(path.relative_to(root)),
                }
            )
    return results
