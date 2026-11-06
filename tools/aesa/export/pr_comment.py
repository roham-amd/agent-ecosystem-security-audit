"""Compact Authority Diff PR comment (≤12 lines).

The product is the PR comment, not the scan report. Target-derived strings are
escaped so findings cannot inject markdown links/mentions into the review UI.
"""

from __future__ import annotations

import re
from typing import Any

from aesa.security.decision import compute_decision, coverage_score_line
from aesa.security.gating import is_gate_finding, is_high_gate_finding

# Escape markdown specials *except* hyphen inside finding IDs (F-004).
_MD_SPECIAL = re.compile(r"([\\`*_{}\[\]()#+.!|>])")
_URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
_MENTION_RE = re.compile(r"(^|[^/\w])@[\w-]+")


def escape_markdown(value: str, *, max_len: int = 160) -> str:
    """Neutralize markdown/HTML injection from target-controlled strings."""
    text = str(value or "").replace("\r", " ").replace("\n", " ").strip()
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
    if risk_delta:
        changes = risk_delta.get("changes") or {}
        for key in ("high_or_critical_new_findings", "gated_new_findings"):
            items = changes.get(key)
            if isinstance(items, list) and items:
                new_powers = [f for f in items if isinstance(f, dict) and is_gate_finding(f)]
                break
    if not new_powers:
        new_powers = [f for f in findings if is_high_gate_finding(f)] or [
            f for f in findings if is_gate_finding(f)
        ]

    lines = [
        "### authdiff Authority Diff",
        f"**Decision:** `{decision}`",
    ]
    if summary:
        lines.append(
            "New gated findings: "
            f"{int(summary.get('gated_findings_added') or 0)} "
            f"(high/critical: {int(summary.get('high_or_critical_findings_added') or 0)})"
        )
    else:
        gated_n = sum(1 for f in findings if is_gate_finding(f))
        lines.append(f"Gated findings on head: {gated_n} (supply `--baseline` for a true diff)")

    lines.append("**New authority / destinations:**")
    if not new_powers:
        lines.append("- (none gated)")
    else:
        shown = new_powers[:5]
        for finding in shown:
            where = _entry(finding)
            where_bit = f" (`{escape_markdown(where, max_len=48)}`)" if where else ""
            fix = _fix(finding)
            fix_bit = f" Fix: {escape_markdown(fix, max_len=60)}" if fix else ""
            # Finding IDs are trusted scanner output — do not backslash-escape hyphens.
            lines.append(
                f"- `{_fid(finding)}` [{escape_markdown(_sev(finding), max_len=12)}] "
                f"{escape_markdown(_title(finding))}{where_bit}.{fix_bit}"
            )
        remaining = len(new_powers) - len(shown)
        if remaining > 0:
            lines.append(f"- +{remaining} more (see findings.json)")

    lines.append(escape_markdown(coverage_score_line(coverage), max_len=200))
    lines.append(
        "_CAPABILITY is inventory. Only SECURITY_FINDING / EXPOSURE gate CI. No findings ≠ safe._"
    )

    # Hard cap: drop lowest-value lines first while keeping header + decision.
    while len(lines) > max_lines and len(lines) > 4:
        cut_at = 3
        if cut_at < len(lines) - 2:
            lines.pop(cut_at)
        else:
            break
    return "\n".join(lines) + "\n"
