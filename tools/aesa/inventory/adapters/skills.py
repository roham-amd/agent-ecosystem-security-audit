from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from aesa.inventory.limits import CollectorLimits

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def discover_skills(
    root: Path,
    *,
    limits: CollectorLimits,
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for path in root.rglob("SKILL.md"):
        if "node_modules" in path.parts or ".git" in path.parts:
            continue
        try:
            rel = path.relative_to(root)
            if len(rel.parts) > limits.max_depth:
                continue
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            events.append({"type": "read_error", "path": str(path), "message": str(exc)})
            continue

        name = path.parent.name
        description = None
        fm = _FRONTMATTER_RE.match(raw)
        if fm:
            for line in fm.group(1).splitlines():
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip().strip('"')
                if line.startswith("description:"):
                    description = line.split(":", 1)[1].strip().strip('"')

        results.append(
            {
                "name": name,
                "type": "Skill",
                "reference_kind": "LOCAL_IMPLEMENTATION",
                "repository_path": str(rel),
                "adapter": "skill_md",
                "adapter_maturity": "supported",
                "discovery_status": "IDENTIFIED",
                "instruction_content_present": True,
                "declared_description": description,
            }
        )
    return results
