from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from aesa.inventory.io import safe_read_text, select_files
from aesa.inventory.jsonc import loads_json_tolerant
from aesa.inventory.limits import CollectorLimits

_SECRETISH_ENV_RE = re.compile(
    r"(api[_-]?key|token|secret|password|passwd|authorization|credential|private[_-]?key)",
    re.IGNORECASE,
)
_DOWNLOAD_EXEC_RE = re.compile(
    r"(curl\s+[^\n|;]*\|\s*(?:sudo\s+)?(?:ba)?sh|"
    r"wget\s+[^\n|;]*\|\s*(?:sudo\s+)?(?:ba)?sh|"
    r"iwr\s+[^\n|;]*\|\s*iex|invoke-webrequest[^\n|;]*\|\s*iex)",
    re.IGNORECASE,
)


def _package_looks_pinned(token: str) -> bool:
    """Distinguish scoped names (`@scope/pkg`) from version pins (`pkg@1.2.3`)."""
    if "@sha256:" in token or "==" in token:
        return True
    if token.startswith("@"):
        # @scope/name → unpinned; @scope/name@1.2.3 → pinned
        return token.count("@") >= 2
    return "@" in token


def _looks_unpinned_launcher(command: str, args: list[Any]) -> bool:
    """True for npx -y / uvx / bunx style launchers without an obvious pin."""
    cmd = command.strip().lower()
    arg_strs = [str(a) for a in args]
    joined = " ".join(arg_strs)
    if cmd in {"npx", "bunx"} and ("-y" in arg_strs or "--yes" in arg_strs):
        pkgs = [a for a in arg_strs if a not in {"-y", "--yes", "--"} and not a.startswith("-")]
        return bool(pkgs) and not any(_package_looks_pinned(p) for p in pkgs)
    if cmd == "uvx":
        return bool(arg_strs) and not any(_package_looks_pinned(a) for a in arg_strs)
    if "npx -y" in f"{cmd} {joined}" or "npx --yes" in f"{cmd} {joined}":
        return not any(_package_looks_pinned(a) for a in arg_strs)
    return False


def _env_has_literal_secret(env: Any) -> bool:
    if not isinstance(env, dict):
        return False
    for key, value in env.items():
        key_s = str(key)
        val_s = str(value) if value is not None else ""
        if not _SECRETISH_ENV_RE.search(key_s):
            continue
        # Placeholder / env expansion is inheritance (RULE-002), not a literal secret.
        if val_s.startswith("${") or val_s.startswith("$(") or val_s.startswith("{{"):
            continue
        if len(val_s) >= 8 and not val_s.startswith("$"):
            return True
    return False


def _env_passes_host_secrets(env: Any) -> bool:
    """True when env keys look credential-shaped and values are host expansions."""
    if not isinstance(env, dict):
        return False
    for key, value in env.items():
        if not _SECRETISH_ENV_RE.search(str(key)):
            continue
        val_s = str(value) if value is not None else ""
        if (
            val_s.startswith("${")
            or val_s.startswith("$(")
            or (val_s.startswith("$") and not val_s.startswith("$$"))
        ):
            return True
    return False


def _is_broad_path_arg(arg: Any) -> bool:
    """True only for root / home / parent-traversal roots — not project abs paths."""
    s = str(arg).strip()
    if not s:
        return False
    lowered = s.lower()
    if lowered in {"/", "~", "$home", "${home}", "%userprofile%", "%homepath%"}:
        return True
    if s.startswith("~/") or s.startswith("~\\"):
        return True
    if s in {".."} or s.startswith("../") or s.startswith("..\\"):
        return True
    # Windows drive root: C:\ or C:/
    if re.fullmatch(r"[A-Za-z]:[\\/]?", s):
        return True
    try:
        parts = Path(s).parts
    except (TypeError, ValueError):
        return False
    return ".." in parts


def _is_mcp_config_candidate(path: Path, root: Path) -> bool:
    rel = path.relative_to(root).as_posix().lower()
    name = path.name.lower()
    if name in {"mcp.json", "mcp_config.json", "mcp_example.json", ".mcp.json"}:
        return True
    if name.endswith(".json") and "mcp" in name:
        return True
    return rel in {".cursor/mcp.json", ".vscode/mcp.json", "mcp.json", ".mcp.json"}


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
        rel = path.relative_to(root).as_posix()
        if raw is None:
            # Oversize / unreadable agent config — fail closed via coverage events.
            events.append(
                {
                    "type": "unparsed_agent_config",
                    "adapter": "mcp_config",
                    "path": rel,
                    "message": "MCP config could not be read (oversize, truncated, or I/O error)",
                }
            )
            continue
        try:
            data = loads_json_tolerant(raw)
        except json.JSONDecodeError as exc:
            events.append(
                {
                    "type": "parse_error",
                    "adapter": "mcp_config",
                    "path": rel,
                    "message": str(exc),
                    "agent_config": True,
                }
            )
            events.append(
                {
                    "type": "unparsed_agent_config",
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
            command = str(cfg.get("command") or "")
            raw_args = cfg.get("args")
            args: list[Any] = list(raw_args) if isinstance(raw_args, list) else []
            if command:
                hints.append("local_command_transport")
                if _looks_unpinned_launcher(command, args):
                    hints.append("unpinned_package_launcher")
            env = cfg.get("env") or cfg.get("environment")
            if env:
                hints.append("sets_environment")
                if _env_has_literal_secret(env):
                    hints.append("literal_secret_in_env")
                elif _env_passes_host_secrets(env):
                    # Only credential-shaped keys with host expansion escalate RULE-002.
                    hints.append("inherits_or_sets_environment")
            url = str(cfg.get("url") or "")
            if url:
                hints.append("remote_endpoint")
                if url.lower().startswith("http://"):
                    hints.append("insecure_http_remote")
            if isinstance(args, list) and any(_is_broad_path_arg(a) for a in args):
                hints.append("broad_or_relative_path_args")
            joined_cmd = f"{command} {' '.join(str(a) for a in args)}"
            if _DOWNLOAD_EXEC_RE.search(joined_cmd):
                hints.append("download_and_execute")
            if any(
                token in joined_cmd.lower()
                for token in (
                    "dangerously-skip-permissions",
                    "bypasspermissions",
                    "--yolo",
                    "skip-permissions",
                )
            ):
                hints.append("permission_bypass_flag")
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
                    "args": list(args) if isinstance(args, list) else [],
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
