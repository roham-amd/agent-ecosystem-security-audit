"""npm-check-updates style dependency pin checker/updater for AESA tools."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

from packaging.version import InvalidVersion, Version

from aesa.paths import repo_root
from aesa.pins import parse_pin_file, parse_pins, replace_pins

_PYPI = "https://pypi.org/pypi/{name}/json"
_USER_AGENT = "aesa-deps/0.3 (+https://github.com/roham-amd/agent-ecosystem-security-audit)"


@dataclass(frozen=True, slots=True)
class PinStatus:
    name: str
    current: str
    latest: str
    outdated: bool
    error: str | None = None


def tools_dir() -> Path:
    return repo_root() / "tools"


def constraints_path() -> Path:
    return tools_dir() / "constraints.txt"


def lock_path() -> Path:
    return tools_dir() / "requirements.lock.txt"


def runtime_req_path() -> Path:
    return tools_dir() / "requirements.txt"


def pyproject_path() -> Path:
    return tools_dir() / "pyproject.toml"


def parse_constraint_pins(text: str | None = None) -> dict[str, str]:
    if text is not None:
        return parse_pins(text)
    return parse_pin_file(constraints_path())


def fetch_latest_version(name: str, *, timeout: float = 20.0) -> str:
    req = urllib.request.Request(
        _PYPI.format(name=name),
        headers={"Accept": "application/json", "User-Agent": _USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    version = payload.get("info", {}).get("version")
    if not version:
        raise RuntimeError(f"PyPI response for {name} missing info.version")
    return str(version)


def _is_outdated(current: str, latest: str) -> bool:
    try:
        return Version(latest) > Version(current)
    except InvalidVersion:
        return current != latest


def _resolve_pin_name(pins: dict[str, str], name: str) -> tuple[str, str] | None:
    if name in pins:
        return name, pins[name]
    match = next((key for key in pins if key.lower() == name.lower()), None)
    if match is None:
        return None
    return match, pins[match]


def check_outdated(*, packages: list[str] | None = None) -> list[PinStatus]:
    pins = parse_constraint_pins()
    names = packages or sorted(pins.keys(), key=str.lower)
    results: list[PinStatus] = []
    for name in names:
        resolved = _resolve_pin_name(pins, name)
        if resolved is None:
            results.append(
                PinStatus(
                    name=name,
                    current="",
                    latest="",
                    outdated=False,
                    error="not in constraints.txt",
                )
            )
            continue
        canon, current = resolved
        try:
            latest = fetch_latest_version(canon)
            results.append(
                PinStatus(
                    name=canon,
                    current=current,
                    latest=latest,
                    outdated=_is_outdated(current, latest),
                )
            )
        except (urllib.error.URLError, TimeoutError, RuntimeError, json.JSONDecodeError) as exc:
            results.append(
                PinStatus(
                    name=canon,
                    current=current,
                    latest="",
                    outdated=False,
                    error=str(exc),
                )
            )
    return results


def _update_pyproject_pins(updates: dict[str, str], *, requires_python: str | None) -> None:
    path = pyproject_path()
    text = path.read_text(encoding="utf-8")
    for name, ver in updates.items():
        text = re.sub(
            rf'("{re.escape(name)}"\s*==\s*")[^"]+(")',
            rf"\g<1>{ver}\g<2>",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            rf'({re.escape(name)}\s*==\s*")[^"]+(")',
            rf"\g<1>{ver}\g<2>",
            text,
            flags=re.IGNORECASE,
        )
    if requires_python:
        text = re.sub(
            r'(requires-python\s*=\s*")[^"]+(")',
            rf"\g<1>{requires_python}\g<2>",
            text,
        )
    path.write_text(text, encoding="utf-8")


def _constraints_document(pins: dict[str, str], *, as_of: date) -> str:
    header = (
        f"# Authoritative pin set for aesa-tools "
        f"(latest compatible from PyPI, {as_of.isoformat()}).\n"
        '# Use with: python -m pip install -c constraints.txt -e ".[dev]"\n'
        "# Update: aesa deps upgrade   |   Check: aesa deps outdated\n"
        "# Minimum Python: >=3.15\n"
        "\n"
    )
    body = "\n".join(f"{name}=={pins[name]}" for name in sorted(pins.keys(), key=str.lower))
    return header + body + "\n"


def upgrade_pins(
    *,
    dry_run: bool = False,
    requires_python: str = ">=3.15",
    as_of: date | None = None,
) -> dict[str, Any]:
    """Bump all constraints to latest PyPI versions (ncu -u equivalent)."""
    as_of = as_of or date.today()
    statuses = check_outdated()
    errors = [status for status in statuses if status.error]
    if errors:
        return {
            "ok": False,
            "dry_run": dry_run,
            "errors": [asdict(err) for err in errors],
            "updated": [],
        }

    updates = {status.name: status.latest for status in statuses}
    changed = [
        {"name": status.name, "from": status.current, "to": status.latest}
        for status in statuses
        if status.outdated or status.current != status.latest
    ]

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "requires_python": requires_python,
            "as_of": as_of.isoformat(),
            "updated": changed,
            "pins": updates,
        }

    constraints_path().write_text(_constraints_document(updates, as_of=as_of), encoding="utf-8")
    lock_path().write_text(
        replace_pins(lock_path().read_text(encoding="utf-8"), updates),
        encoding="utf-8",
    )
    runtime_req_path().write_text(
        replace_pins(runtime_req_path().read_text(encoding="utf-8"), updates),
        encoding="utf-8",
    )
    _update_pyproject_pins(updates, requires_python=requires_python)

    return {
        "ok": True,
        "dry_run": False,
        "requires_python": requires_python,
        "as_of": as_of.isoformat(),
        "updated": changed,
        "pins": parse_constraint_pins(),
    }


def outdated_report() -> dict[str, Any]:
    statuses = check_outdated()
    outdated = [asdict(status) for status in statuses if status.outdated]
    errors = [asdict(status) for status in statuses if status.error]
    return {
        "checked": len(statuses),
        "outdated_count": len(outdated),
        "outdated": outdated,
        "errors": errors,
        "all": [asdict(status) for status in statuses],
        "requires_python_expected": ">=3.15",
    }
