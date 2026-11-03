"""Shared dependency pin parsing for build gates and deps upgrade."""

from __future__ import annotations

import re
from pathlib import Path

_PIN_RE = re.compile(r"^(\s*)([A-Za-z0-9_.\-]+)\s*==\s*([^\s#]+)(.*)$")


def parse_pins(text: str) -> dict[str, str]:
    """Parse ``name==version`` lines; last occurrence wins."""
    pins: dict[str, str] = {}
    for line in text.splitlines():
        match = _PIN_RE.match(line)
        if match:
            pins[match.group(2)] = match.group(3)
    return pins


def parse_pin_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise FileNotFoundError(path)
    return parse_pins(path.read_text(encoding="utf-8"))


def replace_pins(text: str, updates: dict[str, str]) -> str:
    """Replace existing ``name==version`` lines (case-insensitive name match)."""
    lower_map = {key.lower(): value for key, value in updates.items()}
    lines: list[str] = []
    for line in text.splitlines():
        match = _PIN_RE.match(line)
        if not match:
            lines.append(line)
            continue
        indent, name, _current, suffix = match.groups()
        new_ver = lower_map.get(name.lower())
        if new_ver is None:
            lines.append(line)
            continue
        lines.append(f"{indent}{name}=={new_ver}{suffix}")
    ending = "\n" if text.endswith("\n") else ""
    return "\n".join(lines) + ending


def normalize_package_name(name: str) -> str:
    return name.replace("_", "-").lower()
