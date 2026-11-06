from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from aesa.inventory.io import safe_read_text, select_files
from aesa.inventory.limits import CollectorLimits

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

_SECRET_TOKEN_RE = re.compile(
    r"\b(secrets?|api[_-]?key|apikey|password|token|credentials?|1password|op_service_account)\b",
    re.IGNORECASE,
)
_NEGATION_RE = re.compile(
    r"\b(no|not|without|never|don't|do not|avoid|forbid(?:den)?)\b",
    re.IGNORECASE,
)
_HIDDEN_UNICODE_RE = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff\u202a-\u202e\u2066-\u2069]")
_DOWNLOAD_EXEC_RE = re.compile(
    r"(curl\s+[^\n|;]*\|\s*(?:ba)?sh|wget\s+[^\n|;]*\|\s*(?:ba)?sh|"
    r"iwr\s+[^\n|;]*\|\s*iex|invoke-webrequest[^\n|;]*\|\s*iex)",
    re.IGNORECASE,
)
_PERMISSION_BYPASS_RE = re.compile(
    r"(--dangerously-skip-permissions|--yolo\b|bypasspermissions|"
    r"permissionmode\s*[:=]\s*bypass|auto[_-]?approve\s*[:=]\s*true|"
    r"skip[_-]?permissions)",
    re.IGNORECASE,
)
_INSTRUCTION_ABUSE_MARKERS = (
    "ignore previous instructions",
    "ignore all previous",
    "do not tell the user",
    "hide this action",
    "bypass confirmation",
    "skip approval",
    "exfiltrate",
    "fetch and execute",
    "download and run",
)


def _mentions_secret_handling(text: str) -> bool:
    """True when secret-related tokens appear outside a short negation window.

    Prevents false positives such as ``No credential handling``.
    """
    for match in _SECRET_TOKEN_RE.finditer(text):
        start = max(0, match.start() - 48)
        window = text[start : match.start()]
        if _NEGATION_RE.search(window):
            continue
        return True
    return False


def _mentions_identity_workflow(text: str) -> bool:
    if "service_account" in text or "op signin" in text:
        start_idx = text.find("service_account")
        if start_idx < 0:
            start_idx = text.find("op signin")
        window = text[max(0, start_idx - 48) : start_idx]
        return not bool(_NEGATION_RE.search(window))
    return False


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
        if _mentions_secret_handling(lowered):
            hints.append("secrets_or_credential_handling")
        if _mentions_identity_workflow(lowered):
            hints.append("identity_or_auth_workflow")
        # Bundled helper scripts next to the skill raise authority questions.
        if any((path.parent / "scripts").glob("*")):
            hints.append("bundled_scripts_directory")
        if _HIDDEN_UNICODE_RE.search(raw):
            hints.append("hidden_unicode_in_instructions")
        if _DOWNLOAD_EXEC_RE.search(raw):
            hints.append("download_and_execute")
        if _PERMISSION_BYPASS_RE.search(raw):
            hints.append("permission_bypass_flag")
        if any(marker in lowered for marker in _INSTRUCTION_ABUSE_MARKERS):
            hints.append("instruction_abuse_content")

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
