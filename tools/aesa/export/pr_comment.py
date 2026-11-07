"""Compact Authority Diff PR comment (≤12 lines).

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


def render_authority_diff_comment(
    findings_doc: dict[str, Any],
    *,
    risk_delta: dict[str, Any] | None = None,
    authority_delta: dict[str, Any] | None = None,
    authority_snapshot: dict[str, Any] | None = None,
    max_lines: int = 12,
) -> str:
    """Render a short PR body focused on new authority / destinations / controls."""
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
        # Absolute mode only when no baseline was supplied.
        new_powers = [f for f in findings if is_high_gate_finding(f)] or [
            f for f in findings if is_gate_finding(f)
        ]

    # Marker is sticky-comment metadata — not counted toward the ≤12 visible lines.
    visible: list[str] = [
        "### authdiff Authority Diff",
        f"**Decision:** `{decision}`",
    ]
    if summary is not None:
        visible.append(
            "New gated findings: "
            f"{int(summary.get('gated_findings_added') or 0)} "
            f"(high/critical: {int(summary.get('high_or_critical_findings_added') or 0)})"
        )
    else:
        gated_n = sum(1 for f in findings if is_gate_finding(f))
        visible.append(f"Gated findings on head: {gated_n} (use `delta --baseline`)")

    component_lines: list[str] = []
    delta_doc = authority_delta or (risk_delta or {}).get("authority_delta")
    if isinstance(delta_doc, dict):
        component_lines = render_component_delta_lines(delta_doc)
    elif isinstance(risk_delta, dict) and risk_delta.get("component_delta_lines"):
        component_lines = list(risk_delta.get("component_delta_lines") or [])

    visible.append("**New authority / destinations:**")
    if component_lines:
        for line in component_lines[:3]:
            visible.append(f"- {escape_markdown(line, max_len=120)}")
    elif not new_powers:
        if has_baseline:
            visible.append("- (no new authority vs baseline)")
        else:
            visible.append("- (none gated)")
    else:
        shown = new_powers[:3]
        for finding in shown:
            where = _entry(finding)
            where_bit = f" (`{escape_markdown(where, max_len=40)}`)" if where else ""
            fix = _fix(finding)
            fix_bit = f" Fix: {escape_markdown(fix, max_len=48)}" if fix else ""
            visible.append(
                f"- `{_fid(finding)}` [{escape_markdown(_sev(finding), max_len=12)}] "
                f"{escape_markdown(_title(finding))}{where_bit}.{fix_bit}"
            )
        remaining = len(new_powers) - len(shown)
        if remaining > 0:
            visible.append(f"- +{remaining} more (see findings.json)")

    suppressed_n = int(findings_doc.get("suppression_count") or 0)
    if not suppressed_n:
        suppressed_n = sum(1 for f in findings if isinstance(f, dict) and f.get("suppressed"))
    if suppressed_n:
        visible.append(f"Suppressions applied: {suppressed_n}")

    visible.append(escape_markdown(coverage_score_line(coverage), max_len=160))
    visible.append("_Only SECURITY_FINDING / EXPOSURE gate CI. No new findings ≠ safe._")

    while len(visible) > max_lines and len(visible) > 4:
        # Drop middle detail first; keep header, decision, first bullet block, footer.
        cut_at = 3
        if cut_at < len(visible) - 2:
            visible.pop(cut_at)
        else:
            break
    return AUTHDIFF_COMMENT_MARKER + "\n" + "\n".join(visible) + "\n"
