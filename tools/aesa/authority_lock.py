"""Committed AUTHORITY.lock — record-level authority identity for PR review.

``authdiff lock`` writes a sorted canonical lock. ``lock --check`` / ``scan --locked``
regenerates and compares. CODEOWNERS on this file is the intended approval path.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from aesa.broker import load_authority_lock
from aesa.security.authority import (
    build_authority_snapshot,
    logical_authority_id,
)
from aesa.security.engine import run_security_scan
from aesa.versioning import product_version

LOCK_NAME = "AUTHORITY.lock"
LOCK_VERSION = 2


def default_lock_path(root: Path) -> Path:
    return root.resolve() / LOCK_NAME


def _policy_hash(root: Path) -> str | None:
    for name in (".aesa.yml", ".aesa.yaml"):
        path = root / name
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            return f"sha256:{digest}"
    return None


def _record_from_component(
    comp: dict[str, Any], raw: dict[str, Any] | None = None
) -> dict[str, Any]:
    raw = raw or {}
    logical = logical_authority_id(
        {
            "host": comp.get("host"),
            "kind": comp.get("kind"),
            "name": comp.get("name"),
            "path": comp.get("path"),
            "id": comp.get("id"),
        }
    )
    return {
        "id": logical,
        "host": str(comp.get("host") or ""),
        "kind": str(comp.get("kind") or ""),
        "name": str(comp.get("name") or ""),
        "path": str(comp.get("path") or "").replace("\\", "/"),
        "digest": str(raw.get("content_digest") or ""),
        "fingerprint": str(comp.get("fingerprint") or ""),
        "pin_state": str(comp.get("pin_state") or "unknown"),
        "approval_posture": str(comp.get("approval_posture") or "unknown"),
        "capabilities": list(comp.get("capabilities") or []),
        "destinations": list(comp.get("destinations") or []),
        "env_keys": list(raw.get("env_keys") or []),
    }


def build_authority_lock(root: Path) -> dict[str, Any]:
    """Scan ``root`` and return a canonical AUTHORITY.lock document."""
    root = root.resolve()
    scan = run_security_scan(root)
    snapshot = build_authority_snapshot(scan)
    by_fp = {
        str(c.get("fingerprint") or ""): c
        for c in (scan.inventory.get("components") or [])
        if isinstance(c, dict)
    }
    records: list[dict[str, Any]] = []
    for comp in snapshot.get("components") or []:
        if not isinstance(comp, dict):
            continue
        raw = by_fp.get(str(comp.get("fingerprint") or ""), {})
        records.append(_record_from_component(comp, raw))
    records.sort(key=lambda r: (r["kind"], r["path"], r["name"], r["id"]))

    body: dict[str, Any] = {
        "version": LOCK_VERSION,
        "product": "authdiff",
        "product_version": product_version(),
        "repository": str(root),
        "audited_commit": scan.commit,
        "policy_hash": _policy_hash(root),
        "records": records,
        # Broker / snapshot compatibility (tool pins filled by `snapshot`).
        "mcp_tools": {},
        "mcp_servers": {
            r["name"] or r["id"]: {
                "path": r["path"],
                "digest": r["digest"],
                "pin_state": r["pin_state"],
                "allowed": True,
            }
            for r in records
            if r["kind"] == "MCP Server Registration"
        },
    }
    canonical = json.dumps(
        {k: v for k, v in body.items() if k != "lock_hash"},
        sort_keys=True,
        separators=(",", ":"),
    )
    body["lock_hash"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:32]
    return body


def write_authority_lock(root: Path, *, path: Path | None = None) -> tuple[Path, dict[str, Any]]:
    lock = build_authority_lock(root)
    dest = path or default_lock_path(root)
    dest.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return dest, lock


def normalize_lock_for_compare(lock: dict[str, Any]) -> dict[str, Any]:
    """Strip ephemeral fields so regenerate-vs-disk compares are stable."""
    records = []
    for rec in lock.get("records") or []:
        if not isinstance(rec, dict):
            continue
        records.append(
            {
                "id": rec.get("id"),
                "host": rec.get("host"),
                "kind": rec.get("kind"),
                "name": rec.get("name"),
                "path": rec.get("path"),
                "digest": rec.get("digest"),
                "fingerprint": rec.get("fingerprint"),
                "pin_state": rec.get("pin_state"),
                "approval_posture": rec.get("approval_posture"),
                "capabilities": list(rec.get("capabilities") or []),
                "destinations": list(rec.get("destinations") or []),
                "env_keys": list(rec.get("env_keys") or []),
            }
        )
    records.sort(
        key=lambda r: (
            r.get("kind") or "",
            r.get("path") or "",
            r.get("name") or "",
            r.get("id") or "",
        )
    )
    return {
        "version": int(lock.get("version") or 1),
        "policy_hash": lock.get("policy_hash"),
        "records": records,
        "mcp_tools": lock.get("mcp_tools") or {},
    }


def diff_authority_locks(
    base: dict[str, Any],
    head: dict[str, Any],
) -> dict[str, Any]:
    """Line-oriented record diff between two locks."""
    base_n = normalize_lock_for_compare(base)
    head_n = normalize_lock_for_compare(head)
    base_by_id = {str(r["id"]): r for r in base_n["records"] if r.get("id")}
    head_by_id = {str(r["id"]): r for r in head_n["records"] if r.get("id")}

    added = [head_by_id[i] for i in sorted(set(head_by_id) - set(base_by_id))]
    removed = [base_by_id[i] for i in sorted(set(base_by_id) - set(head_by_id))]
    changed: list[dict[str, Any]] = []
    for rid in sorted(set(base_by_id) & set(head_by_id)):
        before, after = base_by_id[rid], head_by_id[rid]
        if before == after:
            continue
        changed.append({"id": rid, "before": before, "after": after})

    policy_changed = base_n.get("policy_hash") != head_n.get("policy_hash")
    lines = render_lock_diff_lines(added=added, removed=removed, changed=changed)
    return {
        "kind": "authority_lock_delta",
        "summary": {
            "records_added": len(added),
            "records_removed": len(removed),
            "records_changed": len(changed),
            "policy_changed": policy_changed,
            "authority_changed": bool(added or removed or changed or policy_changed),
        },
        "changes": {"added": added, "removed": removed, "changed": changed},
        "lines": lines,
    }


def render_lock_diff_lines(
    *,
    added: list[dict[str, Any]],
    removed: list[dict[str, Any]],
    changed: list[dict[str, Any]],
    limit: int = 20,
) -> list[str]:
    lines: list[str] = []
    for rec in added[:limit]:
        pin = rec.get("pin_state") or "unknown"
        caps = ", ".join(rec.get("capabilities") or []) or "authority"
        dest = ", ".join((rec.get("destinations") or [])[:2])
        dest_bit = f", reaches {dest}" if dest else ""
        env = ", ".join((rec.get("env_keys") or [])[:3])
        env_bit = f", passes {env}" if env else ""
        label = rec.get("name") or rec.get("id")
        lines.append(f"+ {rec.get('kind')} `{label}`: {caps}; pin={pin}{dest_bit}{env_bit}")
    for rec in removed[: max(0, limit - len(lines))]:
        label = rec.get("name") or rec.get("id")
        lines.append(f"- {rec.get('kind')} `{label}`")
    for item in changed[: max(0, limit - len(lines))]:
        after = item.get("after") or {}
        label = after.get("name") or item.get("id")
        lines.append(f"~ {after.get('kind')} `{label}` changed")
    return lines


def check_locked(root: Path, *, lock_path: Path | None = None) -> tuple[dict[str, Any], int]:
    """Regenerate lock and compare to the committed file. Exit 1 on drift."""
    root = root.resolve()
    path = lock_path or default_lock_path(root)
    if not path.is_file():
        return {
            "ok": False,
            "error": f"Missing {path.name}",
            "hint": "Run `authdiff lock` and commit AUTHORITY.lock.",
            "lines": [],
        }, 1
    on_disk = load_authority_lock(path)
    current = build_authority_lock(root)
    delta = diff_authority_locks(on_disk, current)
    ok = not delta["summary"]["authority_changed"]
    report = {
        "ok": ok,
        "lock": str(path),
        "delta": delta,
        "lines": delta["lines"],
        "verdict": "LOCKED" if ok else "AUTHORITY_CHANGED",
    }
    return report, 0 if ok else 1


def run_lock_command(
    root: Path,
    *,
    check: bool = False,
    update: bool = False,
    lock_path: Path | None = None,
) -> tuple[str, int]:
    root = root.resolve()
    path = lock_path or default_lock_path(root)
    if check and not update:
        report, code = check_locked(root, lock_path=path)
        if report.get("ok"):
            return f"AUTHORITY.lock matches observed authority ({path.name}).", 0
        lines = report.get("lines") or []
        body = "\n".join(lines) if lines else "(authority changed; re-run `authdiff lock`)"
        return (
            f"AUTHORITY.lock out of date — authority changed, needs owner review.\n{body}",
            code,
        )
    dest, lock = write_authority_lock(root, path=path)
    n = len(lock.get("records") or [])
    action = "Updated" if update or path.exists() else "Wrote"
    return f"{action} {dest} ({n} authority records).", 0
