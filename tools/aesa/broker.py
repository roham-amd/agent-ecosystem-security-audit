"""Authority broker MVP — ``authdiff run -- <server cmd>``.

Scrubs inherited secrets from the child environment and optionally records a
pinned ``AUTHORITY.lock`` path for the child. This is **not** a full MCP
stdio proxy; pair with ``authdiff snapshot`` to pin tool description hashes.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from aesa.process_env import scrub_env


def _loads_object(text: str) -> dict[str, Any]:
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("AUTHORITY lock root must be a JSON object")
    return data


def load_authority_lock(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    name = path.name.lower()
    if suffix == ".json" or name.endswith(".lock.json"):
        return _loads_object(text)
    if suffix in {".yml", ".yaml"} or "lock" in name:
        # Prefer JSON content even in .yml for the MVP (no PyYAML dependency).
        try:
            return _loads_object(text)
        except (json.JSONDecodeError, ValueError):
            return _parse_simple_lock_yaml(text)
    return _loads_object(text)


def _parse_simple_lock_yaml(text: str) -> dict[str, Any]:
    """Parse a tiny AUTHORITY.lock subset without a YAML dependency."""
    tools: dict[str, str] = {}
    in_tools = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped in {"mcp_tools:", "mcp_tools: {}"}:
            in_tools = True
            continue
        if in_tools and line.startswith("  ") and ":" in line:
            key, _, val = stripped.partition(":")
            tools[key.strip()] = val.strip().strip("\"'")
        elif in_tools and not line.startswith((" ", "\t")):
            in_tools = False
    return {"mcp_tools": tools, "version": 1}


def run_brokered(
    command: list[str],
    *,
    lock_path: Path | None = None,
    cwd: Path | None = None,
) -> int:
    if not command:
        raise ValueError("command required after --")
    # Reject shell metacharacters in the executable path segment only — args stay literal.
    exe = command[0]
    if any(ch in exe for ch in ("|", ";", "&", ">", "<", "`", "\n")):
        raise ValueError(f"refusing executable with shell metacharacters: {exe!r}")

    env = scrub_env(extra={"AUTHDIFF_BROKER": "1"})
    lock_meta: dict[str, Any] = {}
    if lock_path is not None:
        lock = load_authority_lock(lock_path)
        pinned = lock.get("mcp_tools") or {}
        lock_meta = {
            "lock": str(lock_path.resolve()),
            "pinned_tools": len(pinned) if isinstance(pinned, dict) else 0,
        }
        env["AUTHDIFF_LOCK"] = str(lock_path.resolve())

    print(
        json.dumps(
            {
                "broker": "authdiff.run",
                "command_argc": len(command),
                "executable": exe,
                "env_key_count": len(env),
                "lock": lock_meta,
                "limitations": [
                    "Environment scrubbed; network/filesystem are NOT sandboxed.",
                    "AUTHORITY.lock is advisory to the child until a full MCP proxy ships.",
                    "Pair with `authdiff snapshot` to pin tool description hashes.",
                ],
            },
            indent=2,
        )
    )
    proc = subprocess.run(
        command,
        check=False,
        cwd=str(cwd) if cwd else None,
        env=env,
    )
    return int(proc.returncode)
