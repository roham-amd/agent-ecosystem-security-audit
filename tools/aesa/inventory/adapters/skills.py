from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from aesa.inventory.io import safe_read_text, select_files
from aesa.inventory.limits import CollectorLimits

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def discover_skills(
    root: Path,
    *,
    files: list[Path],
    limits: CollectorLimits,
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for path in select_files(files, lambda p: p.name == "SKILL.md"):
        raw = safe_read_text(path, root=root, limits=limits, events=events, adapter="skill_md")
        if raw is None:
            continue
        rel = path.relative_to(root)
        name = path.parent.name
        description = None
        fm = _FRONTMATTER_RE.match(raw)
        if fm:
            for line in fm.group(1).splitlines():
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip().strip('"')
                if line.startswith("description:"):
                    description = line.split(":", 1)[1].strip().strip('"')

        hints: list[str] = []
        lowered = raw.lower()
        if "http://" in lowered or "https://" in lowered:
            hints.append("external_url_reference")
        if any(token in lowered for token in ("subprocess", "os.system", "bash ", "powershell")):
            hints.append("possible_code_execution_reference")
        if any(
            token in lowered for token in (".sh", ".ps1", "```python", "```bash", "```powershell")
        ):
            hints.append("script_reference")
        if any(
            token in lowered
            for token in (
                "secret",
                "api_key",
                "apikey",
                "password",
                "token",
                "credential",
                "1password",
                "op_service_account",
            )
        ):
            hints.append("secrets_or_credential_handling")
        if "service_account" in lowered or "op signin" in lowered:
            hints.append("identity_or_auth_workflow")
        # Bundled helper scripts next to the skill raise authority questions.
        if any((path.parent / "scripts").glob("*")):
            hints.append("bundled_scripts_directory")

        results.append(
            {
                "name": name,
                "type": "Skill",
                "reference_kind": "LOCAL_IMPLEMENTATION",
                "repository_path": str(rel).replace("\\", "/"),
                "adapter": "skill_md",
                "adapter_maturity": "SUPPORTED",
                "discovery_status": "IDENTIFIED",
                "instruction_content_present": True,
                "declared_description": description,
                "priority_hints": hints,
            }
        )
    return results
