"""Build evidence records with commit, digest, and line provenance when available."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aesa.security.models import Evidence, EvidenceClass, VerificationStatus
from aesa.supply_chain.digest import sha256_file


@dataclass(slots=True)
class EvidenceContext:
    """Shared scan context for provenance-bound evidence construction."""

    repository_root: Path | None = None
    source_commit: str | None = None
    observed_at: str | None = None


def resolve_source_file(root: Path | None, repository_path: str | None) -> Path | None:
    if root is None or not repository_path:
        return None
    candidate = (root / repository_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    return candidate


def locate_needle_lines(text: str, needle: str | None) -> tuple[int | None, int | None]:
    """Return 1-indexed inclusive line span for the first needle match."""
    if not needle:
        return None, None
    lowered = text.lower()
    target = needle.lower()
    idx = lowered.find(target)
    if idx < 0:
        return None, None
    start_line = text.count("\n", 0, idx) + 1
    end_idx = idx + len(needle)
    end_line = text.count("\n", 0, end_idx) + 1
    return start_line, end_line


def component_content_digest(
    root: Path | None, component: dict[str, Any]
) -> str | None:
    path = resolve_source_file(root, component.get("repository_path"))
    if path is None:
        return None
    return f"sha256:{sha256_file(path)}"


def enrich_component_provenance(
    components: list[dict[str, Any]],
    *,
    root: Path | None,
) -> None:
    """Attach content digests used by fingerprints and evidence producers."""
    for component in components:
        digest = component_content_digest(root, component)
        if digest:
            component["content_digest"] = digest


def build_rule_evidence(
    evidences: list[Evidence],
    *,
    component: dict[str, Any],
    summary: str,
    ctx: EvidenceContext | None = None,
    status: VerificationStatus = "OBSERVED",
    evidence_class: EvidenceClass = "SOURCE_STATIC",
    limitations: list[str] | None = None,
    needle: str | None = None,
    collection_method: str = "deterministic_rule",
) -> Evidence:
    ctx = ctx or EvidenceContext()
    file_path = component.get("repository_path")
    line_start: int | None = None
    line_end: int | None = None
    content_digest = component.get("content_digest")
    source = resolve_source_file(ctx.repository_root, file_path)
    if source is not None:
        if not content_digest:
            content_digest = f"sha256:{sha256_file(source)}"
        if needle:
            try:
                text = source.read_text(encoding="utf-8", errors="replace")
            except OSError:
                text = ""
            line_start, line_end = locate_needle_lines(text, needle)

    eid = f"E-{len(evidences) + 1:03d}"
    ev = Evidence(
        evidence_id=eid,
        component_id=str(component.get("component_id") or "UNKNOWN"),
        evidence_class=evidence_class,
        verification_status=status,
        file_path=file_path,
        line_start=line_start,
        line_end=line_end,
        content_digest=content_digest,
        collection_method=collection_method,
        source_commit=ctx.source_commit,
        observed_at=ctx.observed_at,
        summary=summary,
        limitations=limitations
        or [
            "Static configuration observation only; host effective permissions not verified.",
        ],
    )
    evidences.append(ev)
    return ev
