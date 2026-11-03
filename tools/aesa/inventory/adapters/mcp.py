from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aesa.inventory.io import safe_read_text, select_files
from aesa.inventory.limits import CollectorLimits


def _is_mcp_config_candidate(path: Path, root: Path) -> bool:
    rel = path.relative_to(root).as_posix().lower()
    name = path.name.lower()
    if name in {"mcp.json", "mcp_config.json", "mcp_example.json"}:
        return True
    if name.endswith(".json") and "mcp" in name:
        return True
    return rel in {".cursor/mcp.json", ".vscode/mcp.json", "mcp.json"}


def _is_mcp_server_source(path: Path) -> bool:
    name = path.name.lower()
    if not name.endswith((".py", ".ts", ".js", ".mjs")):
        return False
    if "mcp" in name:
        return True
    parts = {p.lower() for p in path.parts}
    return "mcp" in parts and name.endswith((".py", ".ts", ".js", ".mjs"))


def discover_mcp_configs(
    root: Path,
    *,
    files: list[Path],
    limits: CollectorLimits,
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for path in select_files(files, lambda p: _is_mcp_config_candidate(p, root)):
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

        if not isinstance(data, dict):
            continue
        servers = data.get("mcpServers") or data.get("servers") or {}
        if not isinstance(servers, dict) or not servers:
            # Candidate filename but not an MCP registration document.
            continue

        example_like = "example" in path.name.lower()
        for name, cfg in servers.items():
            if not isinstance(cfg, dict):
                continue
            hints: list[str] = []
            if example_like:
                hints.append("example_or_template_config")
            if cfg.get("command"):
                hints.append("local_command_transport")
            if cfg.get("env") or cfg.get("environment"):
                hints.append("inherits_or_sets_environment")
            if cfg.get("url"):
                hints.append("remote_endpoint")
            args = cfg.get("args")
            if isinstance(args, list) and any(
                ".." in str(a) or str(a).startswith("/") for a in args
            ):
                hints.append("broad_or_relative_path_args")
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
                }
            )

    # MCP server implementations (source), distinct from client registration JSON.
    for path in select_files(files, _is_mcp_server_source):
        raw = safe_read_text(
            path, root=root, limits=limits, events=events, adapter="mcp_server_source"
        )
        if raw is None:
            continue
        lowered = raw.lower()
        name_has_mcp = "mcp" in path.name.lower()
        has_protocol_marker = any(
            token in lowered
            for token in ("fastmcp", "mcp.server", "@modelcontextprotocol", "mcp = ")
        )
        if not name_has_mcp and not has_protocol_marker:
            continue

        rel = path.relative_to(root).as_posix()
        server_hints: list[str] = ["mcp_server_source"]
        if "urllib" in lowered or "requests." in lowered or "httpx" in lowered:
            server_hints.append("network_client_in_server")
        if "write_bytes" in lowered or ("open(" in lowered and '"w' in lowered):
            server_hints.append("filesystem_write_capability_reference")
        if "subprocess" in lowered or "os.system" in lowered:
            server_hints.append("possible_code_execution_reference")
        if "github.com" in lowered or "api.github.com" in lowered:
            server_hints.append("github_fetch_capability")

        results.append(
            {
                "name": path.stem,
                "type": "MCP Server Implementation",
                "reference_kind": "LOCAL_IMPLEMENTATION",
                "repository_path": rel,
                "adapter": "mcp_server_source",
                "adapter_maturity": "PARTIAL",
                "discovery_status": "IDENTIFIED",
                "priority_hints": server_hints,
            }
        )

    return results
