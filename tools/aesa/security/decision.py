"""Gate decision labels for reports, PR comments, and agent digests.

Decisions are derived from gated findings + coverage honesty — never a trust score.
"""

from __future__ import annotations

from typing import Any, Literal

from aesa.security.gating import HIGH_SEVERITIES, is_gate_finding, is_high_gate_finding

Decision = Literal["BLOCK", "REVIEW", "PASS-WITH-COVERAGE-GAPS"]


def compute_decision(
    findings: list[Any],
    *,
    coverage: dict[str, Any] | None = None,
    risk_delta: dict[str, Any] | None = None,
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

    # Never emit a bare PASS — incomplete coverage is the honest default.
    return "PASS-WITH-COVERAGE-GAPS"


def decision_sentences(
    decision: Decision,
    findings: list[Any],
    *,
    risk_delta: dict[str, Any] | None = None,
) -> list[str]:
    """Three short sentences explaining the decision (report lead)."""
    gated = [f for f in findings if is_gate_finding(f)]
    high = [f for f in gated if _severity(f) in HIGH_SEVERITIES]
    added = int((risk_delta or {}).get("gated_findings_added") or 0)

    if decision == "BLOCK":
        lead = (
            f"BLOCK: {len(high)} high/critical authority issue(s) require a fix or "
            "explicit risk acceptance before merge/install."
        )
    elif decision == "REVIEW":
        lead = (
            f"REVIEW: {len(gated)} gated finding(s) need human judgment "
            "(not automatically merge-blocking at fail-on=high)."
        )
    else:
        lead = (
            "PASS-WITH-COVERAGE-GAPS: no gated SECURITY_FINDING/EXPOSURE fired; "
            "incomplete adapters mean this is not a security clearance."
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

    action = "Next: `aesa explain F-00N` for evidence, or `aesa harden` for dry-run fix patches."
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
    if total == 0:
        return "Coverage: no adapter-classified components (treat as gap, not safety)."
    pct = round(100 * supported / total) if total else 0
    return (
        f"Coverage: {pct}% SUPPORTED ({supported}/{total}); "
        f"PARTIAL={partial} MANUAL_ONLY={manual} — clean result ≠ safe."
    )


def _severity(finding: Any) -> str:
    if isinstance(finding, dict):
        return str(finding.get("severity") or "")
    return str(finding.severity)


def _class(finding: Any) -> str:
    if isinstance(finding, dict):
        return str(finding.get("finding_class") or "")
    return str(finding.finding_class)
