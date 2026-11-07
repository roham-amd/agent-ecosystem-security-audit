"""Compact Authority Diff PR comment (≤12 lines).

Answers five questions immediately:
1. What changed?
2. What new authority does it introduce?
3. What evidence supports that claim?
4. What is unknown?
5. What decision or action is required?

The product is the PR comment, not the scan report. Target-derived strings are
escaped so findings cannot inject markdown links/mentions into the review UI.
"""

from __future__ import annotations

import re
from typing import Any

from aesa.security.authority import render_component_delta_lines
from aesa.security.decision import compute_decision, coverage_score_line
from aesa.security.gating import is_gate_finding, is_high_gate_finding

# Escape markdown specials *except* hyphen inside finding IDs (F-004).
_MD_SPECIAL = re.compile(r"([\\`*_{}\[\]()#+.!|>])")
_URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
_MENTION_RE = re.compile(r"(^|[^/\w])@[\w-]+")

# Sticky-comment marker for `gh pr comment --edit-last` / create-or-update flows.
AUTHDIFF_COMMENT_MARKER = "<!-- authdiff-authority-diff -->"


def escape_markdown(value: str, *, max_len: int = 160) -> str:
    """Neutralize markdown/HTML injection from target-controlled strings."""
    text = str(value or "").replace("\r", " ").replace("\n", " ").strip()
    # Strip terminal/OSC control sequences as well as markdown.
    text = re.sub(r"\x1b\[[0-9;]*[A-Za-z]|\x1b\][^\x07]*\x07", "", text)
    text = _URL_RE.sub("[redacted-url]", text)
    text = _MENTION_RE.sub(r"\1[@]", text)
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    text = _MD_SPECIAL.sub(r"\\\1", text)
    if len(text) > max_len:
        text = text[: max_len - 1] + "…"
    return text


def _title(finding: Any) -> str:
    if isinstance(finding, dict):
        return str(finding.get("title") or finding.get("finding_id") or "finding")
    return str(finding.title)


def _fid(finding: Any) -> str:
    if isinstance(finding, dict):
        return str(finding.get("finding_id") or "")
    return str(finding.finding_id)


def _sev(finding: Any) -> str:
    if isinstance(finding, dict):
        return str(finding.get("severity") or "")
    return str(finding.severity)


def _entry(finding: Any) -> str:
    if isinstance(finding, dict):
        return str(finding.get("entry_point") or "")
    return str(getattr(finding, "entry_point", "") or "")


def _fix(finding: Any) -> str:
    if isinstance(finding, dict):
        return str(finding.get("fix_snippet") or finding.get("recommended_action") or "")
    return str(
        getattr(finding, "fix_snippet", "") or getattr(finding, "recommended_action", "") or ""
    )


def _evidence_ids(finding: Any) -> list[str]:
    if isinstance(finding, dict):
        raw = finding.get("evidence_ids") or finding.get("evidence") or []
    else:
        raw = getattr(finding, "evidence_ids", None) or getattr(finding, "evidence", None) or []
    out: list[str] = []
    for item in raw:
        if isinstance(item, str) and item:
            out.append(item)
        elif isinstance(item, dict):
            eid = item.get("evidence_id") or item.get("id")
            if eid:
                out.append(str(eid))
    return out


def _unknowns_line(coverage: dict[str, Any]) -> str:
    not_verified = coverage.get("not_verified") or []
    manual = coverage.get("manual_review_families") or []
    unparsed = int(coverage.get("unparsed_agent_config_count") or 0)
    bits: list[str] = []
    if isinstance(not_verified, list) and not_verified:
        labels = []
        for item in not_verified[:2]:
            if isinstance(item, dict):
                labels.append(str(item.get("family") or item.get("surface") or item))
            else:
                labels.append(str(item))
        bits.append("NOT VERIFIED: " + ", ".join(labels))
    if isinstance(manual, list) and manual:
        bits.append("MANUAL_ONLY: " + ", ".join(str(x) for x in manual[:2]))
    if unparsed:
        bits.append(f"UNPARSED={unparsed}")
    if not bits:
        return "Unknown: runtime / host-effective permissions not assessed"
    return "Unknown: " + "; ".join(bits)


def _required_action(decision: str, new_powers: list[Any], lock_lines: list[str]) -> str:
    if decision == "BLOCK":
        return "Required: remediate high/critical authority, then re-run gate"
    if decision == "REVIEW":
        if new_powers:
            fix = _fix(new_powers[0])
            if fix:
                return f"Required: {fix}"
            return "Required: review gated findings and approve or narrow authority"
        if lock_lines:
            return "Required: CODEOWNERS review of AUTHORITY.lock update"
        return "Required: review coverage gaps / unparsed configs"
    return "Required: no gated action — still review Unknowns before merge"


def render_authority_diff_comment(
    findings_doc: dict[str, Any],
    *,
    risk_delta: dict[str, Any] | None = None,
    authority_delta: dict[str, Any] | None = None,
    authority_snapshot: dict[str, Any] | None = None,
    lock_delta: dict[str, Any] | None = None,
    max_lines: int = 12,
) -> str:
    """Render a short PR body focused on the five Authority Diff questions."""
    del authority_snapshot  # reserved for future evidence drill-down
    findings = list(findings_doc.get("findings") or [])
    coverage = findings_doc.get("coverage") or {}
    summary = (risk_delta or {}).get("summary") if risk_delta else None
    if summary is None and risk_delta and "gated_findings_added" in risk_delta:
        summary = risk_delta
    decision = compute_decision(findings, coverage=coverage, risk_delta=summary)

    new_powers: list[Any] = []
    has_baseline = risk_delta is not None
    if risk_delta:
        changes = risk_delta.get("changes") or {}
        for key in ("high_or_critical_new_findings", "gated_new_findings"):
            items = changes.get(key)
            if isinstance(items, list) and items:
                new_powers = [f for f in items if isinstance(f, dict) and is_gate_finding(f)]
                break
    elif not has_baseline:
        new_powers = [f for f in findings if is_high_gate_finding(f)] or [
            f for f in findings if is_gate_finding(f)
        ]

    component_lines: list[str] = []
    delta_doc = authority_delta or (risk_delta or {}).get("authority_delta")
    if isinstance(delta_doc, dict):
        component_lines = render_component_delta_lines(delta_doc)
    elif isinstance(risk_delta, dict) and risk_delta.get("component_delta_lines"):
        component_lines = list(risk_delta.get("component_delta_lines") or [])

    lock_lines: list[str] = []
    lock_summary: dict[str, Any] = {}
    if isinstance(lock_delta, dict):
        lock_lines = list(lock_delta.get("lines") or [])
        lock_summary = dict(lock_delta.get("summary") or {})

    # Marker is sticky-comment metadata — not counted toward the ≤12 visible lines.
    visible: list[str] = [
        "### authdiff Authority Diff",
        f"**Decision:** `{decision}`",
    ]

    # 1. What changed?
    changed_bits: list[str] = []
    if lock_summary:
        for label, key in (
            ("expansions", "expansions"),
            ("reductions", "reductions"),
            ("replacements", "replacements"),
            ("representations", "representations"),
        ):
            n = int(lock_summary.get(key) or 0)
            if n:
                changed_bits.append(f"{n} {label}")
        if lock_summary.get("policy_changed"):
            changed_bits.append("policy")
    if summary is not None:
        changed_bits.append(f"{int(summary.get('gated_findings_added') or 0)} gated findings")
    if not changed_bits and component_lines:
        changed_bits.append(f"{len(component_lines)} component delta(s)")
    if not changed_bits:
        changed_bits.append(
            "no authority delta vs baseline" if has_baseline else "absolute head scan"
        )
    visible.append("**Changed:** " + escape_markdown(", ".join(changed_bits), max_len=140))

    # 2. What new authority?
    visible.append("**New authority:**")
    authority_bullets: list[str] = []
    for line in (lock_lines or component_lines)[:2]:
        authority_bullets.append(f"- {escape_markdown(line, max_len=120)}")
    if not authority_bullets and new_powers:
        finding = new_powers[0]
        where = _entry(finding)
        where_bit = f" (`{escape_markdown(where, max_len=40)}`)" if where else ""
        authority_bullets.append(
            f"- `{_fid(finding)}` [{escape_markdown(_sev(finding), max_len=12)}] "
            f"{escape_markdown(_title(finding))}{where_bit}"
        )
        if len(new_powers) > 1:
            authority_bullets.append(f"- +{len(new_powers) - 1} more gated findings")
    if not authority_bullets:
        authority_bullets.append("- (none gated)")
    visible.extend(authority_bullets)

    # 3. Evidence
    evidence: list[str] = []
    for finding in new_powers[:3]:
        evidence.extend(_evidence_ids(finding)[:2])
        fid = _fid(finding)
        if fid:
            evidence.append(fid)
    evidence = list(dict.fromkeys(evidence))[:4]
    if evidence:
        visible.append(
            "**Evidence:** " + ", ".join(f"`{escape_markdown(e, max_len=24)}`" for e in evidence)
        )
    else:
        visible.append("**Evidence:** see `findings.json` / lock diff lines")

    # 4. Unknown
    visible.append(escape_markdown(_unknowns_line(coverage), max_len=160))

    # 5. Required action
    visible.append(escape_markdown(_required_action(decision, new_powers, lock_lines), max_len=160))

    suppressed_n = int(findings_doc.get("suppression_count") or 0)
    if not suppressed_n:
        suppressed_n = sum(1 for f in findings if isinstance(f, dict) and f.get("suppressed"))
    if suppressed_n and len(visible) < max_lines:
        visible.append(f"Suppressions retained: {suppressed_n}")

    if len(visible) < max_lines:
        visible.append(escape_markdown(coverage_score_line(coverage), max_len=140))

    while len(visible) > max_lines and len(visible) > 6:
        # Drop middle detail first; keep header, decision, authority, footer action.
        cut_at = 4
        if cut_at < len(visible) - 2:
            visible.pop(cut_at)
        else:
            break
    return AUTHDIFF_COMMENT_MARKER + "\n" + "\n".join(visible) + "\n"
