"""Stable component fingerprints for baseline identity (rename-resistant when content is hashed)."""

from __future__ import annotations

import hashlib
from typing import Any


def component_fingerprint(component: dict[str, Any]) -> str:
    """Return a short fingerprint preferring content digest over path.

    Identity priority:
    1. type + adapter + content_digest (stable across renames/moves of identical bytes)
    2. type + adapter + name + repository_path (fallback when digest unavailable)

    Identical content at two paths shares a fingerprint (content clones). Path is an
    attribute tracked separately in baselines, not part of digest-backed identity.
    """
    ctype = str(component.get("type") or "").strip()
    adapter = str(component.get("adapter") or "").strip()
    digest = str(component.get("content_digest") or "").strip()
    name = str(component.get("name") or "").strip().lower()
    path = str(component.get("repository_path") or "").strip().replace("\\", "/")

    if digest:
        material = f"{ctype}|{adapter}|{digest}"
    else:
        material = f"{ctype}|{adapter}|{name}|{path}"

    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def finding_key(rule_id: str, fingerprint: str | None = None, component_ids: list[str] | None = None) -> str:
    """Stable finding identity for risk deltas.

    Prefer rule + content fingerprint so renames / component_id reshuffles do not
    look like new findings. Fall back to rule + component ids when no fingerprint.
    """
    if fingerprint:
        return f"{rule_id}:{fingerprint}"
    comps = ",".join(sorted(component_ids or []))
    return f"{rule_id}:{comps}"


def paths_by_fingerprint(components: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Map fingerprint → sorted repository paths (supports content clones)."""
    mapping: dict[str, set[str]] = {}
    for component in components:
        fp = str(component.get("fingerprint") or component_fingerprint(component))
        path = str(component.get("repository_path") or component.get("name") or "").replace(
            "\\", "/"
        )
        mapping.setdefault(fp, set()).add(path)
    return {fp: sorted(paths) for fp, paths in sorted(mapping.items())}
