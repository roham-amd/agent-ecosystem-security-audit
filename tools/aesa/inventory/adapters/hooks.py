from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aesa.inventory.io import safe_read_text, select_files
from aesa.inventory.limits import CollectorLimits

_HOOK_NAMES = {"hooks.json", "hooks.yaml", "hooks.yml"}


def discover_hooks(
    root: Path,
    *,
    files: list[Path],
    limits: CollectorLimits,
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for path in select_files(
        files,
        lambda p: (
            p.name in _HOOK_NAMES
            or (p.parent.name == "hooks" and p.suffix in {".json", ".md", ".py"})
        ),
    ):
        raw = safe_read_text(path, root=root, limits=limits, events=events, adapter="hooks")
        if raw is None:
            continue
        rel = path.relative_to(root).as_posix()
        hints: list[str] = []
        lowered = raw.lower()
        if any(token in lowered for token in ("before", "pretool", "pre-tool", "sessionstart")):
            hints.append("pre_execution_lifecycle")
        if any(token in lowered for token in ("command", "shell", "exec", "subprocess")):
            hints.append("possible_execution_boundary")
        if any(
            token in lowered
            for token in ("curl ", "wget ", "invoke-webrequest", "iwr ", "| sh", "| bash")
        ):
            hints.append("download_and_execute")

        name = path.stem
        if path.suffix == ".json":
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                events.append(
                    {
                        "type": "parse_error",
                        "adapter": "hooks",
                        "path": rel,
                        "message": str(exc),
                    }
                )
                continue

            if isinstance(data, dict) and "hooks" in data and isinstance(data["hooks"], dict):
                for hook_name in data["hooks"]:
                    results.append(
                        {
                            "name": str(hook_name),
                            "type": "Hook",
                            "reference_kind": "LOCAL_CONFIGURATION_OR_INSTRUCTIONS",
                            "repository_path": rel,
                            "adapter": "hooks",
                            "adapter_maturity": "PARTIAL",
                            "discovery_status": "IDENTIFIED",
                            "priority_hints": list(hints),
                        }
                    )
                continue

        results.append(
            {
                "name": name,
                "type": "Hook",
                "reference_kind": "LOCAL_CONFIGURATION_OR_INSTRUCTIONS",
                "repository_path": rel,
                "adapter": "hooks",
                "adapter_maturity": "PARTIAL",
                "discovery_status": "IDENTIFIED",
                "priority_hints": hints,
            }
        )
    return results
