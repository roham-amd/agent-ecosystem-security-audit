"""Gate decision labels for reports, PR comments, and agent digests.

Decisions are derived from gated findings + coverage honesty — never a trust score.
"""

from __future__ import annotations

from typing import Any, Literal

from aesa.security.gating import HIGH_SEVERITIES, is_gate_finding, is_high_gate_finding

# Legacy alias kept for one release so old fixtures/docs still parse.
Decision = Literal[
    "BLOCK",
    "REVIEW",
    "NO-GATED-FINDINGS",
    "PASS-WITH-COVERAGE-GAPS",  # deprecated alias of NO-GATED-FINDINGS
]

_AGENT_CONFIG_MARKERS = (
    "mcp.json",
    ".mcp.json",
    "mcp_config",
    ".claude/",
    ".cursor/",
    ".vscode/mcp",
    "hooks.json",
    "settings.json",
    "SKILL.md",
)


def unparsed_agent_config_count(
    coverage: dict[str, Any] | None = None,
    parser_events: list[dict[str, Any]] | None = None,
) -> int:
    """Count agent-config parse/skip events that must fail closed."""
    cov = coverage or {}
    if "unparsed_agent_config_count" in cov:
        return int(cov.get("unparsed_agent_config_count") or 0)
    events = parser_events or cov.get("parser_events") or []
    count = 0
    for event in events:
        if not isinstance(event, dict):
            continue
        etype = str(event.get("type") or "")
        path = str(event.get("path") or "").replace("\\", "/").lower()
        if etype == "unparsed_agent_config":
            count += 1
            continue
        if etype in {
            "parse_error",
            "parse_skipped_size",
            "skipped_oversize",
            "file_too_large",
        } and _looks_agent_config(path):
            count += 1
    return count


def _looks_agent_config(path: str) -> bool:
    return any(marker in path for marker in _AGENT_CONFIG_MARKERS)


def compute_decision(
    findings: list[Any],
    *,
    coverage: dict[str, Any] | None = None,
    risk_delta: dict[str, Any] | None = None,
    parser_events: list[dict[str, Any]] | None = None,
) -> Decision:
    """Return the operator-facing decision for a scan or risk delta."""
    if risk_delta:
        if risk_delta.get("high_or_critical_findings_added"):
            return "BLOCK"
        if risk_delta.get("gated_findings_added"):
            return "REVIEW"

    gated = [f for f in findings if is_gate_finding(f)]
    if any(is_high_gate_finding(f) for f in gated):
        return "BLOCK"
    if gated:
        return "REVIEW"

    # Unparsed / oversize agent configs fail closed as REVIEW — never a quiet pass.
    if unparsed_agent_config_count(coverage, parser_events) > 0:
        return "REVIEW"

    # Never emit a bare PASS — incomplete coverage is the honest default.
    return "NO-GATED-FINDINGS"


def decision_sentences(
    decision: Decision,
    findings: list[Any],
    *,
    risk_delta: dict[str, Any] | None = None,
    coverage: dict[str, Any] | None = None,
) -> list[str]:
    """Three short sentences explaining the decision (report lead)."""
    gated = [f for f in findings if is_gate_finding(f)]
    high = [f for f in gated if _severity(f) in HIGH_SEVERITIES]
    added = int((risk_delta or {}).get("gated_findings_added") or 0)
    unparsed = unparsed_agent_config_count(coverage)
    cov_line = coverage_score_line(coverage)

    # Normalize deprecated alias for messaging.
    label = "NO-GATED-FINDINGS" if decision == "PASS-WITH-COVERAGE-GAPS" else decision

    if label == "BLOCK":
        lead = (
            f"BLOCK: {len(high)} high/critical authority issue(s) require a fix or "
            "explicit risk acceptance before merge/install."
        )
    elif label == "REVIEW":
        if unparsed and not gated:
            lead = (
                f"REVIEW: {unparsed} agent-config file(s) were unparsed or oversize "
                "(fail closed — not a clearance)."
            )
        else:
            lead = (
                f"REVIEW: {len(gated)} gated finding(s) need human judgment "
                "(not automatically merge-blocking at fail-on=high)."
            )
    else:
        lead = (
            f"NO-GATED-FINDINGS ({cov_line.split(';')[0].replace('Coverage: ', 'coverage ')}): "
            "no gated SECURITY_FINDING/EXPOSURE fired; this is not a security clearance."
        )

    if risk_delta is not None:
        delta = (
            f"Authority diff vs baseline: {added} new gated finding(s), "
            f"{int(risk_delta.get('high_or_critical_findings_added') or 0)} high/critical."
        )
    else:
        delta = (
            f"Observed {len(gated)} gated finding(s) and "
            f"{sum(1 for f in findings if _class(f) == 'CAPABILITY')} capability observation(s)."
        )

    action = "Next: `aesa explain F-00N` for evidence, or `aesa fix` for dry-run fix patches."
    return [lead, delta, action]


def coverage_score_line(coverage: dict[str, Any] | None) -> str:
    """One-line coverage honesty for reports (not a trust score)."""
    cov = coverage or {}
    maturity = cov.get("component_counts_by_maturity") or {}
    if not isinstance(maturity, dict):
        maturity = {}
    supported = int(maturity.get("SUPPORTED") or 0)
    partial = int(maturity.get("PARTIAL") or 0)
    manual = int(maturity.get("MANUAL_ONLY") or 0)
    total = supported + partial + manual + int(maturity.get("UNSUPPORTED") or 0)
    unparsed = int(cov.get("unparsed_agent_config_count") or 0)
    if total == 0 and unparsed == 0:
        return "Coverage: no adapter-classified components (treat as gap, not safety)."
    pct = round(100 * supported / total) if total else 0
    base = (
        f"Coverage: {pct}% SUPPORTED ({supported}/{total}); PARTIAL={partial} MANUAL_ONLY={manual}"
    )
    if unparsed:
        base += f"; UNPARSED={unparsed}"
    return base + " — clean result ≠ safe."


def _severity(finding: Any) -> str:
    if isinstance(finding, dict):
        return str(finding.get("severity") or "")
    return str(finding.severity)


def _class(finding: Any) -> str:
    if isinstance(finding, dict):
        return str(finding.get("finding_class") or "")
    return str(finding.finding_class)
